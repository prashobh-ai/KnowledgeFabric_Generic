"""Generic tabular connector — CSV/JSON records become retrievable knowledge.

Replaces the Nova-specific FDA connector. One connector covers the whole class
of "can you also pull from our database / CRM / Salesforce" asks, because every
one of those systems exports CSV. Point it at a folder of exports and each row
becomes a KnowledgeRecord.

The verbalisation step matters and is easy to get wrong. A raw row —
{"policy":"MP-0142","status":"active"} — is invisible to both lexical and
semantic retrieval. Rendered as a sentence it is retrievable by the identical
machinery that serves the document corpus, which is the whole point of a fabric.
Typed facets are preserved separately for filtering and graph construction, so
nothing is lost by verbalising.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterator

from .base import KnowledgeRecord, sanitize


class TabularConnector:
    name = "Structured Records"
    source_type = "structured"

    def __init__(self, root: Path, tenant: str = ""):
        self.root = Path(root)
        self.tenant = tenant

    def _rows(self) -> Iterator[tuple[str, dict]]:
        if not self.root.exists():
            return
        for path in sorted(self.root.glob("*.csv")):
            with open(path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    yield path.stem, row
        for path in sorted(self.root.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            rows = data if isinstance(data, list) else data.get("records", [])
            for row in rows:
                if isinstance(row, dict):
                    yield path.stem, row

    def fetch(self) -> Iterator[KnowledgeRecord]:
        for table, row in self._rows():
            clean = {k: sanitize(v) for k, v in row.items() if sanitize(v)}
            if not clean:
                continue
            key = next(iter(clean.values()))
            # Verbalise: field/value pairs become a readable sentence so the
            # record competes on the same terms as prose.
            parts = [f"{k.replace('_', ' ')} is {v}" for k, v in clean.items()]
            text = (f"Record {key} from the {table.replace('_', ' ')} dataset. "
                    + ". ".join(parts) + ".")
            yield KnowledgeRecord(
                source_type=self.source_type,
                source_system=f"{table.replace('_', ' ').title()} export",
                source_id=f"{table}:{key}",
                title=f"{table.replace('_', ' ').title()} — {key}",
                text=text,
                section_path=["Structured Records", table.replace("_", " ").title()],
                url="",
                metadata={"record_type": "structured_row", "table": table, **clean},
                entities=[("Record", str(key))],
            )
