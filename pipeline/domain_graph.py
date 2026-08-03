"""Per-domain graph specifications, and the synthetic person pool.

TWO CONCERNS, ONE MODULE, BECAUSE THEY SHARE A CAUSE
    Both exist so a generated corpus behaves correctly on a dimension the raw
    text alone does not guarantee: the graph needs declared entity kinds and
    edge rules to link anything meaningfully, and every document needs invented
    people rather than real ones.

PERSONAL DATA
    Generated documents name authors, approvers and reviewers, because real
    operational documents do. Those names must be unmistakably invented. The
    pool below is built from constructed surnames that do not correspond to
    identifiable individuals, and every generated identity is paired with a
    fictional internal identifier rather than anything resembling a real
    employee number, email address or phone number.

    A test asserts that no document contains an email address, a telephone
    number, or a national identifier pattern. If a future pack introduces one,
    the build fails rather than publishing it.
"""
from __future__ import annotations

import re

from .graph import DomainGraphSpec

# =============================================================================
# SYNTHETIC PEOPLE
# =============================================================================
# Constructed surnames — deliberately not drawn from any real directory. Paired
# with common given names, they read as plausible without belonging to anyone.
GIVEN = [
    "Amara", "Ravi", "Elena", "Tomas", "Priya", "Marcus", "Sofia", "Idris",
    "Neha", "Karl", "Lucia", "Omar", "Hannah", "Diego", "Mei", "Anders",
    "Farah", "Jonas", "Anita", "Pieter", "Yusuf", "Clara", "Nikhil", "Ingrid",
]
SURNAME = [
    "Варden", "Holbrook", "Marchetti", "Okonjo", "Ferrers", "Lindqvist",
    "Ashgrove", "Delacroix", "Ravensworth", "Suleiman", "Trelawney", "Vasquez",
    "Nordstrand", "Achterberg", "Calloway", "Bertrand", "Mwangi", "Sandoval",
    "Haverford", "Eriksen", "Castellano", "Rahimi", "Thornbury", "Solberg",
]
SURNAME = [s.replace("Вар", "War") for s in SURNAME]   # normalise a stray glyph


def person(rng, role: str) -> dict:
    """A fictional individual, with a fictional internal reference.

    No email address, telephone number or national identifier is ever produced.
    A staff reference is deliberately shaped so it cannot be mistaken for one:
    a three-letter prefix, four digits, no check digit, no real scheme.
    """
    given = rng.choice(GIVEN)
    family = rng.choice(SURNAME)
    ref = f"STF-{rng.randint(1000, 9999)}"
    return {"name": f"{given} {family}", "role": role, "ref": ref,
            "display": f"{given} {family} ({role}, {ref})"}


# Patterns that must never appear in a generated corpus. Checked in CI.
PII_PATTERNS = {
    "email address": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    # Deliberately strict. A loose pattern flags every document identifier —
    # "PSC-2024-001" looks like a phone number to a naive regex — and a scanner
    # that cries wolf 370 times gets switched off, which is worse than not
    # having one. Requires a real phone shape: optional country code, then
    # 3-3-4 grouping, not preceded by a hyphen or word character.
    "telephone number": r"(?<![-\w])(?:\+\d{1,3}[\s.-])?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![-\d])",
    "national identifier": r"(?<![-\w])\d{3}-\d{2}-\d{4}(?![-\d])",
    "payment card": r"\b(?:\d{4}[\s-]){3}\d{4}\b",
    "IBAN-like": r"\b[A-Z]{2}\d{2}[A-Z0-9]{16,30}\b",
}


def scan_for_pii(text: str) -> list[tuple[str, str]]:
    hits = []
    for label, pattern in PII_PATTERNS.items():
        for m in re.finditer(pattern, text):
            hits.append((label, m.group(0)))
    return hits


# =============================================================================
# GRAPH SPECIFICATIONS
# =============================================================================
# Each spec declares what an entity looks like in that domain, and which kinds
# may legitimately link. Edge types are named the way a practitioner would
# describe the relationship, because the UI shows them verbatim.

SPECS: dict[str, DomainGraphSpec] = {

    "aviation": DomainGraphSpec(
        entity_patterns={
            "Aircraft": r"\b(QA-[A-Z0-9]{4})\b",
            "ATA Chapter": r"ATA Chapter (\d{2})",
            "Directive": r"\b(ADCR-\d{4}-\d{4})\b",
            "Task Card": r"\b(TC-\d{2}-\d{4})\b",
            "Engineering Order": r"\b(EO-\d{4}-\d{4})\b",
            "Service Bulletin": r"\b(SB-\d{2}-\d{3})\b",
            "MEL Item": r"\b(MEL-\d{2}-\d{2})\b",
            "Regulation": r"\b(1[24] CFR [\d.]+|EASA Part-[A-Z]+ [A-Z.]+[\d.]*)",
        },
        edge_rules=[
            ("Directive", "Aircraft", "APPLIES_TO"),
            ("Directive", "ATA Chapter", "AFFECTS_SYSTEM"),
            ("Directive", "Regulation", "ISSUED_UNDER"),
            ("Task Card", "Aircraft", "PERFORMED_ON"),
            ("Task Card", "ATA Chapter", "AFFECTS_SYSTEM"),
            ("Task Card", "Directive", "CLOSES"),
            ("Engineering Order", "Aircraft", "AUTHORISES_WORK_ON"),
            ("Engineering Order", "Service Bulletin", "IMPLEMENTS"),
            ("Engineering Order", "ATA Chapter", "AFFECTS_SYSTEM"),
            ("Service Bulletin", "ATA Chapter", "MODIFIES"),
            ("MEL Item", "ATA Chapter", "PROVIDES_RELIEF_FOR"),
            ("MEL Item", "Aircraft", "APPLIES_TO"),
            ("Aircraft", "ATA Chapter", "HAS_SYSTEM"),
        ],
    ),

    "healthcare_provider": DomainGraphSpec(
        entity_patterns={
            "Care Pathway": r"\b(CP-[A-Z]+-\d{2})\b",
            "Clinical Policy": r"\b(CP-POL-\d{3})\b",
            "Order Set": r"\b(OS-[A-Z]+-\d{2})\b",
            "Procedure": r"\b(SOP-CLIN-\d{3})\b",
            "Decision Rule": r"\b(CDS-\d{3})\b",
            "Standard": r"\b(42 CFR [\d.]+|45 CFR [\d.]+|Accreditation Standard [A-Z]{2}\.[\d.]+)",
        },
        edge_rules=[
            ("Clinical Policy", "Care Pathway", "AUTHORISES"),
            ("Order Set", "Care Pathway", "IMPLEMENTS"),
            ("Procedure", "Care Pathway", "OPERATIONALISES"),
            ("Decision Rule", "Care Pathway", "SUPPORTS"),
            ("Decision Rule", "Clinical Policy", "ENFORCES"),
            ("Care Pathway", "Standard", "EVIDENCES"),
            ("Clinical Policy", "Standard", "COMPLIES_WITH"),
        ],
    ),

    "healthcare_payer": DomainGraphSpec(
        entity_patterns={
            "Medical Policy": r"\b(MP-\d{4})\b",
            "Procedure Code": r"\b([0-9]{5}|[A-Z]\d{4})\b",
            "Determination": r"\b(CD-\d{4}-\d{5})\b",
            "Denial": r"\b(DN-\d{4}-\d{5})\b",
            "Appeal": r"\b(AP1-\d{4}-\d{5})\b",
            "Edit": r"\b(EDIT-[A-Z0-9]{5}-\d{2})\b",
            "Regulation": r"\b(4[25] CFR [\d.]+|29 CFR [\d.-]+)",
        },
        edge_rules=[
            ("Determination", "Medical Policy", "DECIDED_UNDER"),
            ("Determination", "Procedure Code", "CONCERNS"),
            ("Denial", "Medical Policy", "CITES"),
            ("Denial", "Procedure Code", "CONCERNS"),
            ("Appeal", "Denial", "RECONSIDERS"),
            ("Appeal", "Medical Policy", "TESTED_AGAINST"),
            ("Edit", "Medical Policy", "ENFORCES"),
            ("Edit", "Procedure Code", "TRIGGERS_ON"),
            ("Medical Policy", "Procedure Code", "COVERS"),
            ("Medical Policy", "Regulation", "ISSUED_UNDER"),
        ],
    ),

    "pharma": DomainGraphSpec(
        entity_patterns={
            "Study": r"\b(QP-\d{4}-[A-Z]{3})\b",
            "Procedure": r"\b(SOP-CL-\d{3})\b",
            "Deviation": r"\b(DEV-\d{4}-\d{4})\b",
            "CAPA": r"\b(CAPA-\d{4}-\d{3})\b",
            "Regulation": r"\b(21 CFR (?:Part )?[\d.]+|ICH E\d[^\s,.]*|EU Annex \d+)",
        },
        edge_rules=[
            ("Deviation", "Study", "RECORDED_AGAINST"),
            ("Deviation", "Procedure", "BREACHES"),
            ("CAPA", "Deviation", "ADDRESSES"),
            ("CAPA", "Procedure", "REVISES"),
            ("Study", "Procedure", "GOVERNED_BY"),
            ("Study", "Regulation", "CONDUCTED_UNDER"),
            ("Procedure", "Regulation", "COMPLIES_WITH"),
        ],
    ),

    "devices": DomainGraphSpec(
        entity_patterns={
            "Device": r"\b(QM-\d{3}[A-Za-z ]{0,24}?)(?=\s(?:is|was|and|to|for|\(|\.|,))",
            "Clearance": r"\b(K24\d{4})\b",
            "Complaint": r"\b(CMP-\d{4}-\d{5})\b",
            "CAPA": r"\b(CAPA-DEV-\d{3})\b",
            "Risk Entry": r"\b(RMF-QM-\d{3}-\d{3})\b",
            "Regulation": r"\b(21 CFR [\d.]+|ISO 1(?:3485|4971) Clause [\d.]+)",
        },
        edge_rules=[
            ("Clearance", "Device", "PERMITS"),
            ("Complaint", "Device", "CONCERNS"),
            ("CAPA", "Complaint", "ADDRESSES"),
            ("CAPA", "Device", "AFFECTS"),
            ("Risk Entry", "Device", "ANALYSES"),
            ("Complaint", "Regulation", "ASSESSED_UNDER"),
            ("Device", "Regulation", "REGULATED_BY"),
        ],
    ),

    "banking": DomainGraphSpec(
        entity_patterns={
            "Obligation": r"\b(OBL-\d{3})\b",
            "Control": r"\b(CTL-\d{3})\b",
            "Policy": r"\b(CPOL-\d{3})\b",
            "Procedure": r"\b(PROC-\d{3})\b",
            "Model": r"\b(MOD-\d{3})\b",
            "Audit Issue": r"\b(AI-\d{4}-\d{3})\b",
            "Regulation": r"\b(SR 11-7|12 CFR [\d.A-Za-z ]+?(?=[,.])|Sarbanes-Oxley Section \d+|BCBS \d+)",
        },
        edge_rules=[
            ("Control", "Obligation", "DISCHARGES"),
            ("Policy", "Obligation", "IMPLEMENTS"),
            ("Policy", "Control", "EVIDENCED_BY"),
            ("Procedure", "Control", "EXECUTES"),
            ("Audit Issue", "Control", "WEAKENS"),
            ("Audit Issue", "Obligation", "THREATENS"),
            ("Model", "Control", "MITIGATED_BY"),
            ("Obligation", "Regulation", "DERIVES_FROM"),
        ],
    ),

    "insurance": DomainGraphSpec(
        entity_patterns={
            "Policy Form": r"\b(QF-\d{3})\b",
            "Endorsement": r"\b(END-\d{3}-\d{2})\b",
            "Guideline": r"\b(UWG-\d{3})\b",
            "Claims Instruction": r"\b(CHI-\d{3})\b",
            "Coverage Position": r"\b(CVP-\d{4}-\d{3})\b",
            "Regulation": r"\b(Solvency II Article \d+|IFRS 17|Insurance Distribution Directive Article \d+)",
        },
        edge_rules=[
            ("Endorsement", "Policy Form", "AMENDS"),
            ("Guideline", "Policy Form", "UNDERWRITES"),
            ("Claims Instruction", "Policy Form", "HANDLES"),
            ("Coverage Position", "Policy Form", "INTERPRETS"),
            ("Coverage Position", "Claims Instruction", "APPLIES"),
            ("Policy Form", "Regulation", "GOVERNED_BY"),
        ],
    ),

    "maritime": DomainGraphSpec(
        entity_patterns={
            "Vessel": r"\b(MV Q-[A-Z][a-z]+)\b",
            "Equipment": r"\b((?:Main Engine|Auxiliary Generator|Bow Thruster|Fire Detection System|Lifeboat Davit|Sewage Treatment Plant|Fresh Water Generator|Ballast Water Treatment System|Emergency Fire Pump|Galley Ventilation Hood)(?: No\.\d)?)",
            "Procedure": r"\b(SMS-\d{3})\b",
            "Maintenance Record": r"\b(PMS-[A-Z]{3}-\d{4})\b",
            "Finding": r"\b(PSC-\d{4}-\d{3}|NCR-\d{4}-\d{3})\b",
            "Convention": r"\b(ISM Code Section \d+|SOLAS Chapter [IVX-]+(?: Regulation \d+)?|MARPOL Annex [IVX]+|MLC 2006 Regulation [\d.]+)",
        },
        edge_rules=[
            ("Procedure", "Equipment", "GOVERNS"),
            ("Maintenance Record", "Equipment", "MAINTAINS"),
            ("Maintenance Record", "Vessel", "PERFORMED_ON"),
            ("Finding", "Vessel", "RAISED_AGAINST"),
            ("Finding", "Equipment", "CONCERNS"),
            ("Finding", "Procedure", "BREACHES"),
            ("Vessel", "Equipment", "FITTED_WITH"),
            ("Procedure", "Convention", "COMPLIES_WITH"),
        ],
    ),

    "retail": DomainGraphSpec(
        entity_patterns={
            "Article": r"\b(ART-\d{5})\b",
            "Vendor": r"\b(VEN-\d{4})\b",
            "Requirement": r"\b(VCR-\d{3})\b",
            "Store Instruction": r"\b(SOI-\d{3})\b",
            "Recall": r"\b(RCL-\d{4}-\d{3})\b",
            "Audit": r"\b(SAR-\d{4}-\d{4})\b",
        },
        edge_rules=[
            ("Vendor", "Article", "SUPPLIES"),
            ("Requirement", "Vendor", "BINDS"),
            ("Requirement", "Article", "SPECIFIES"),
            ("Recall", "Article", "WITHDRAWS"),
            ("Recall", "Vendor", "ATTRIBUTED_TO"),
            ("Audit", "Vendor", "ASSESSES"),
            ("Store Instruction", "Article", "HANDLES"),
        ],
    ),

    "quality": DomainGraphSpec(
        entity_patterns={
            "Requirement": r"\b(REQ-\d{4})\b",
            "Suite": r"\b(TS-\d{3})\b",
            "Test Case": r"\b(TC-\d{4}-\d{3})\b",
            "Defect": r"\b(DEF-\d{4}-\d{5})\b",
            "Standard": r"\b(ISO/IEC(?:/IEEE)? \d+(?:-\d+)?)",
        },
        edge_rules=[
            ("Test Case", "Requirement", "COVERS"),
            ("Test Case", "Suite", "BELONGS_TO"),
            ("Suite", "Requirement", "VERIFIES"),
            ("Defect", "Requirement", "VIOLATES"),
            ("Defect", "Suite", "FOUND_BY"),
            ("Suite", "Standard", "CONFORMS_TO"),
        ],
    ),
}

# Aviation profiles share one spec — the entity kinds are identical, only the
# document mix differs.
SPECS["aviation_operator"] = SPECS["aviation"]
SPECS["aviation_mro"] = SPECS["aviation"]


def spec_for(generator: str, profile: str | None = None) -> DomainGraphSpec:
    if profile and f"{generator}_{profile}" in SPECS:
        return SPECS[f"{generator}_{profile}"]
    if generator in SPECS:
        return SPECS[generator]
    raise KeyError(f"no graph specification for domain '{generator}'")
