"""Document connector — wraps the existing Phase 1 parsers behind the Connector contract.

Deliberately thin: parsers.py already handles PDF/DOCX/MD/TXT with heading-aware
structure. This adapts its output to KnowledgeRecords and classifies each file into
a knowledge domain so the fabric can reason about provenance.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from ..parsers import iter_sources, parse_any
from .base import KnowledgeRecord

# Folder name -> (source_system label, domain facet)
DOMAIN_MAP = {
    "fda_regulatory": ("FDA Clearance Documents", "Regulatory"),
}
DEFAULT_DOMAIN = ("Nova IFU Library", "Product Documentation")


def _classify(path: Path, root: Path) -> tuple[str, str]:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return DEFAULT_DOMAIN
    top = rel.parts[0] if len(rel.parts) > 1 else ""
    return DOMAIN_MAP.get(top, DEFAULT_DOMAIN)


def _infer_product(name: str) -> str:
    n = name.lower()
    for key, label in [
        ("statstrip_2.0", "StatStrip Glucose (Gen 2)"),
        ("statstrip_xpress", "StatStrip Xpress2 Glucose"),
        ("statstrip_glucose", "StatStrip Glucose"),
        ("statstrip_lactate", "StatStrip Lactate"),
        ("statsensor", "StatSensor Creatinine"),
        ("lactate_plus", "Lactate Plus"),
        ("prime_plus", "Stat Profile Prime Plus"),
        ("prime_es", "Stat Profile Prime ES Comp Plus"),
        ("allegro", "Nova Allegro"),
        ("nova_primary", "Nova Primary Glucose Analyzer"),
        ("nova_max", "Nova Max"),
    ]:
        if key in n:
            return label
    return "Unclassified"


def _header_fields(text: str) -> dict:
    """Generated documents declare their own identity in a header block. Every
    chunk of the document must carry that identity, not just the header chunk.

    Without this the graph cannot form a single typed edge: a document's own
    identifier sits in its first chunk while the identifiers it CITES sit in
    later chunks, so the two never co-occur and no relationship is ever
    observed. Attaching identity at document level is what makes
    "this task card closes that directive" a fact the graph can hold.
    """
    # The markdown parser strips emphasis markers, so the header arrives as
    # plain "Document number: X Document type: Y Owner: Z" on one line. Match
    # that, not the source markup.
    import re
    out = {}
    m = re.search(r"Document number:\s*(\S+)", text or "")
    if m:
        out["doc_id"] = m.group(1).strip()
    m = re.search(r"Document type:\s*(.+?)(?=\s+(?:Owner|Approved|Revision|Effective):|$)",
                  text or "")
    if m:
        out["doc_type"] = m.group(1).strip()
    m = re.search(r"Owner:\s*(.+?)(?=\s+(?:Approved|Revision|Effective):|$)", text or "")
    if m:
        out["owner"] = m.group(1).strip()
    return out


def _doc_type_from_text(text: str) -> str:
    """Generated documents declare their own type in the header. Trust that
    over any filename heuristic — a filename is a guess, a declaration is not."""
    import re
    m = re.search(r"\*\*Document type:\*\*\s*(.+)", text or "")
    return m.group(1).strip() if m else ""


def _infer_doc_type(name: str) -> str:
    n = name.lower()
    if "_review_" in n:
        return "FDA Review Memorandum"
    if n.startswith("k") and n[1:3].isdigit():
        return "FDA 510(k) Summary"
    if "quick_reference" in n or "reference_manual" in n:
        return "Quick Reference Guide"
    if "ifu" in n or "instruction" in n:
        return "Instructions For Use"
    return "Document"


# Maps a declared document type onto the graph entity kind that represents it.
# Anything unmapped still becomes a node — as a Document — so nothing is lost.
DOC_TYPE_KIND = {
    "Airworthiness Directive Compliance Record": "Directive",
    "Maintenance Task Card": "Task Card",
    "Engineering Order": "Engineering Order",
    "Service Bulletin": "Service Bulletin",
    "Minimum Equipment List Entry": "MEL Item",
    "Clinical Care Pathway": "Care Pathway",
    "Clinical Policy": "Clinical Policy",
    "Order Set Specification": "Order Set",
    "Standard Operating Procedure": "Procedure",
    "Decision Support Rule Specification": "Decision Rule",
    "Medical Policy": "Medical Policy",
    "Coverage Determination": "Determination",
    "Denial Notice": "Denial",
    "Appeal Determination": "Appeal",
    "Adjudication Edit Specification": "Edit",
    "Clinical Study Protocol": "Study",
    "Protocol Deviation Record": "Deviation",
    "CAPA Record": "CAPA",
    "Instructions for Use": "Device",
    "510(k) Summary": "Clearance",
    "Complaint Record": "Complaint",
    "Risk Management File Entry": "Risk Entry",
    "Regulatory Obligation Record": "Obligation",
    "Internal Control Description": "Control",
    "Credit Policy Section": "Policy",
    "Procedure Document": "Procedure",
    "Model Documentation": "Model",
    "Audit Issue": "Audit Issue",
    "Policy Wording": "Policy Form",
    "Endorsement": "Endorsement",
    "Underwriting Guideline": "Guideline",
    "Claims Handling Instruction": "Claims Instruction",
    "Coverage Position": "Coverage Position",
    "Safety Management System Procedure": "Procedure",
    "Planned Maintenance Record": "Maintenance Record",
    "Port State Control Finding": "Finding",
    "Non-Conformity Report": "Finding",
    "Vendor Compliance Requirement": "Requirement",
    "Product Specification": "Article",
    "Store Operating Instruction": "Store Instruction",
    "Product Recall Notice": "Recall",
    "Supplier Audit Report": "Audit",
    "Test Case Specification": "Test Case",
    "Test Plan": "Suite",
    "Defect Report": "Defect",
}


def _kind_for(doc_type: str) -> str:
    return DOC_TYPE_KIND.get(doc_type, "Document")


class DocumentConnector:
    name = "Document Library"
    source_type = "document"

    def __init__(self, root: Path):
        self.root = Path(root)

    def fetch(self) -> Iterator[KnowledgeRecord]:
        for path in iter_sources(self.root):
            try:
                parsed = parse_any(path)
            except Exception as exc:  # one bad file must not kill the fabric
                print(f"  ! skip {path.name}: {exc}")
                continue

            system, domain = _classify(path, self.root)
            product = _infer_product(path.name)
            header = _header_fields("\n".join(p.text for p in parsed.paragraphs[:10]))
            doc_type = header.get("doc_type") or _infer_doc_type(path.name)
            k_number = path.name.split("_")[0] if path.name.startswith("K") else ""

            for para in parsed.paragraphs:
                if len(para.text) < 40:      # drop page furniture
                    continue
                yield KnowledgeRecord(
                    source_type=self.source_type,
                    source_system=system,
                    source_id=f"{path.name}#p{para.paragraph_index}",
                    title=parsed.name,
                    text=para.text,
                    section_path=para.section_path,
                    page=para.page,
                    url="",
                    metadata={
                        "record_type": "document_paragraph",
                        "document_name": parsed.name,
                        "domain": domain,
                        "product": product,
                        "doc_type": doc_type,
                        "k_number": k_number,
                        "page_count": parsed.page_count,
                        "paragraph_index": para.paragraph_index,
                        "source_path": str(path),
                        "doc_id": header.get("doc_id", ""),
                        "doc_type": doc_type,
                        "owner": header.get("owner", ""),
                    },
                    # The document's OWN identifier, on every chunk. This is the
                    # anchor that lets a citation elsewhere in the document form
                    # a real edge rather than an unlinked mention.
                    entities=([(_kind_for(doc_type), header["doc_id"])]
                              if header.get("doc_id") else []),
                )
