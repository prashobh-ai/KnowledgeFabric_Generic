"""Healthcare provider domain pack — clinical / EMR side.

Deliberately paired with pack_healthcare_payer.py. The two are the clearest
demonstration of the subtype rule: same industry label, almost no shared
vocabulary, documents, systems, regulators or questions.

    provider (this pack)      pathways, order sets, clinical policy, accreditation
                              SNOMED CT, LOINC, ICD-10-CM, HL7 FHIR
                              CMS Conditions of Participation, accreditation standards

    payer (the other pack)    medical policy, coverage determination, denials
                              CPT/HCPCS, MS-DRG, X12 837/835/270/271
                              claims adjudication and appeal rights

Showing both side by side in one demo is the fastest way to make the point that
"healthcare" is not a configuration.

THE SPINE: care pathway identifier + clinical policy number. A CMIO navigates by
the pathway; the policy is what authorises it; the order set is how it reaches
the bedside. All three must name the same identifiers.
"""
from .engine import DomainPack

REGS = [
    ("42 CFR 482.13", "patient rights under the Conditions of Participation"),
    ("42 CFR 482.21", "quality assessment and performance improvement programme"),
    ("42 CFR 482.24", "medical record services and content requirements"),
    ("42 CFR 482.23", "nursing services and staffing requirements"),
    ("45 CFR 164.312", "technical safeguards for electronic protected health information"),
    ("45 CFR 164.308", "administrative safeguards and workforce access management"),
    ("Accreditation Standard IC.02.01.01", "infection prevention and control activities"),
    ("Accreditation Standard MM.05.01.01", "medication order review before dispensing"),
    ("Accreditation Standard PC.01.02.03", "assessment and reassessment of patients"),
    ("Accreditation Standard RC.01.03.01", "medical record entry authentication and timeliness"),
]

SYSTEMS = [
    "the electronic health record", "the computerised provider order entry module",
    "the clinical decision support engine", "the pharmacy verification queue",
    "the results review workspace", "the care management registry",
    "the clinical documentation improvement queue", "the accreditation evidence repository",
]

ROLES = [
    "Chief Medical Information Officer", "Director of Nursing Practice",
    "Clinical Informatics Lead", "Pharmacy and Therapeutics Chair",
    "Quality and Patient Safety Director", "Medical Staff Committee Chair",
    "Clinical Governance Lead", "Health Information Management Director",
    "Infection Prevention Lead", "Care Pathway Owner",
]

PATHWAYS = [
    ("CP-SEPSIS-01", "Adult Sepsis Recognition and Response"),
    ("CP-CHF-04", "Heart Failure Admission and Transition"),
    ("CP-STROKE-02", "Acute Stroke Assessment"),
    ("CP-COPD-03", "COPD Exacerbation Management"),
    ("CP-AKI-01", "Acute Kidney Injury Surveillance"),
    ("CP-VTE-02", "Venous Thromboembolism Prophylaxis"),
    ("CP-DELIR-01", "Delirium Screening and Prevention"),
    ("CP-PAIN-05", "Multimodal Analgesia"),
    ("CP-DIAB-02", "Inpatient Glycaemic Management"),
    ("CP-PNEU-01", "Community Acquired Pneumonia"),
    ("CP-FALLS-03", "Falls Risk Assessment"),
    ("CP-DISCH-01", "Discharge Readiness and Follow-up"),
]

VOCAB = {
    "observation": [
        "a documented early warning score above the escalation threshold",
        "a serum lactate result returned above the reference range",
        "a change in level of consciousness recorded on reassessment",
        "an unexplained reduction in urine output over the preceding interval",
        "a medication reconciliation discrepancy identified at admission",
        "an incomplete allergy record at the point of order entry",
    ],
    "intervention": [
        "escalate to the responsible clinician within the stated interval",
        "initiate the associated order set through the order entry module",
        "repeat the assessment and document the outcome in the record",
        "refer to the specialist team using the standard referral pathway",
        "review the medication list against the reconciliation record",
        "document the rationale where the pathway is not followed",
    ],
    "interval": [
        "within 60 minutes of recognition",
        "within one nursing shift",
        "at each documented reassessment",
        "before the next scheduled medication round",
        "within 24 hours of admission",
    ],
    "measure": [
        "the proportion of eligible patients with the assessment completed on time",
        "the median interval from recognition to first intervention",
        "the rate of pathway variance with documented rationale",
        "the proportion of records with authenticated entries within the required period",
    ],
}

QUESTIONS = [
    "What is the escalation threshold on the sepsis pathway?",
    "Which order set implements the heart failure pathway?",
    "Who is responsible for approving a change to a clinical pathway?",
    "What must be documented when the pathway is not followed?",
    "How quickly must medication reconciliation be completed after admission?",
    "Which accreditation standard covers medication order review?",
    "What are the record authentication requirements?",
    "Which policy governs the delirium screening pathway?",
    "How is pathway compliance measured?",
    "What triggers escalation on the acute kidney injury pathway?",
    "Which conditions of participation apply to the medical record?",
    "How often must the falls risk assessment be repeated?",
]


def _pathway_scope(ctx):
    return (
        f"This care pathway describes the assessment, escalation and documentation "
        f"expected for patients meeting the entry criteria for {ctx['pathway_name']} "
        f"({ctx['pathway']}) across all inpatient areas of {ctx['tenant']}.\n\n"
        f"The pathway is authorised by clinical policy {ctx['policy']} and implemented "
        f"through order set {ctx['ref']('Order Set Specification')} in {ctx['system']}. "
        f"Bedside execution follows {ctx['ref']('Standard Operating Procedure')}.\n\n"
        f"Entry criterion: {ctx['observation']}. On recognition, staff must "
        f"{ctx['intervention']} {ctx['interval']}."
    )


def _pathway_variance(ctx):
    return (
        f"Clinical judgement takes precedence over the pathway. Where the pathway is not "
        f"followed, the responsible clinician must document the rationale in the record.\n\n"
        f"Variance is reviewed monthly by the {ctx['approver']}. The reported measure is "
        f"{ctx['measure']}.\n\n"
        f"Sustained variance without documented rationale is escalated through the quality "
        f"assessment and performance improvement programme under {ctx['reg'][0]}."
    )


def _policy_statement(ctx):
    return (
        f"{ctx['tenant']} maintains clinical policy {ctx['policy']} governing the conduct "
        f"of care described in the {ctx['pathway_name']} pathway ({ctx['pathway']}).\n\n"
        f"It is the policy of the organisation that {ctx['observation']} results in a "
        f"documented clinical response. Staff must {ctx['intervention']} {ctx['interval']}.\n\n"
        f"Regulatory basis: {ctx['reg'][0]} — {ctx['reg'][1]}."
    )


def _policy_resp(ctx):
    return (
        f"The {ctx['role']} owns this policy and is accountable for its currency. "
        f"Review occurs at least every two years, or sooner where practice, evidence or "
        f"regulation changes.\n\n"
        f"The {ctx['approver']} approves substantive revisions. Approved revisions are "
        f"published to {ctx['system']} and the superseded version is retained in the "
        f"accreditation evidence repository."
    )


def _orderset(ctx):
    return (
        f"Order set supporting the {ctx['pathway_name']} pathway ({ctx['pathway']}), "
        f"deployed in {ctx['system']}.\n\n"
        f"This set implements pathway {ctx['pathway']} under clinical policy {ctx['policy']}, "
        f"supported by decision rule {ctx['ref']('Decision Support Rule Specification')}. "
        f"It is presented to the ordering clinician when {ctx['observation']}. "
        f"Default selections reflect the pathway; each may be deselected with a documented "
        f"reason.\n\n"
        f"Contents include the initial assessment bundle, the associated laboratory "
        f"requests, and the escalation task routed to the responsible clinician "
        f"{ctx['interval']}.\n\n"
        f"Changes to this order set require approval by the {ctx['approver']} and are "
        f"validated in the non-production environment before release."
    )


def _sop_procedure(ctx):
    r = ctx["rng"]
    steps = [
        f"Confirm the patient meets the entry criteria for {ctx['pathway']}.",
        f"Record the assessment in {ctx['system']} using the structured template.",
        f"Where {ctx['observation']}, {ctx['intervention']}.",
        f"Repeat the assessment {ctx['interval']} until the criteria are no longer met.",
        "Document the outcome, including any deviation and its rationale.",
    ]
    return "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))


def _accred_evidence(ctx):
    return (
        f"Evidence prepared in support of {ctx['reg'][0]} — {ctx['reg'][1]}.\n\n"
        f"The organisation demonstrates compliance through clinical policy {ctx['policy']} "
        f"and the associated {ctx['pathway_name']} pathway ({ctx['pathway']}).\n\n"
        f"Sampled records show that {ctx['intervention']} was performed {ctx['interval']} "
        f"in the majority of eligible episodes. The reported measure is {ctx['measure']}.\n\n"
        f"Gaps identified during the internal survey are tracked to closure by the "
        f"{ctx['approver']}."
    )


def _audit_finding(ctx):
    return (
        f"Internal clinical audit of the {ctx['pathway_name']} pathway ({ctx['pathway']}).\n\n"
        f"Observation: in a sample of records, {ctx['observation']} was present without a "
        f"documented response, contrary to clinical policy {ctx['policy']} and pathway "
        f"{ctx['pathway']}. Procedure reference: {ctx['ref']('Standard Operating Procedure')}.\n\n"
        f"Standard: {ctx['reg'][0]} — {ctx['reg'][1]}.\n\n"
        f"Required action: reinforce that staff must {ctx['intervention']} {ctx['interval']}, "
        f"and re-audit at the next cycle. Owner: {ctx['role']}."
    )


def _cds_rule(ctx):
    return (
        f"Decision support rule supporting clinical policy {ctx['policy']} and the "
        f"{ctx['pathway_name']} pathway ({ctx['pathway']}).\n\n"
        f"Enforces clinical policy {ctx['policy']} for pathway {ctx['pathway']}, alongside "
        f"order set {ctx['ref']('Order Set Specification')}.\n\n"
        f"Trigger: {ctx['observation']}.\n\n"
        f"Action: present an interruptive advisory to the ordering clinician recommending "
        f"that they {ctx['intervention']}. The advisory records the response, including "
        f"override and the reason given.\n\n"
        f"Override rates are monitored by the {ctx['approver']}; a sustained rate above "
        f"threshold triggers review of the rule for alert burden."
    )


def _governance(ctx):
    return (
        f"Minute of the committee reviewing clinical policy {ctx['policy']} and the "
        f"associated {ctx['pathway_name']} pathway ({ctx['pathway']}).\n\n"
        f"The committee noted {ctx['measure']} and the level of documented variance. "
        f"Discussion focused on whether {ctx['observation']} is being recognised reliably "
        f"at the point of care.\n\n"
        f"Decision: the pathway is reaffirmed without substantive change. The "
        f"{ctx['role']} will report the measure again at the next meeting."
    )


DOC_TYPES = [
    {"name": "Clinical Care Pathway", "count_share": 1.4,
     "id": lambda c: c["pathway"],
     "title": lambda c: f"Care Pathway — {c['pathway_name']}",
     "sections": [("Scope and Entry Criteria", _pathway_scope),
                  ("Variance and Review", _pathway_variance)]},

    {"name": "Clinical Policy", "count_share": 1.4,
     "id": lambda c: c["policy"],
     "title": lambda c: f"Clinical Policy — {c['pathway_name']}",
     "sections": [("Policy Statement", _policy_statement),
                  ("Responsibilities and Review", _policy_resp)]},

    {"name": "Order Set Specification", "count_share": 1.2,
     "id": lambda c: f"OS-{c['pathway'].split('-')[1]}-{c['idx'] % 40:02d}",
     "title": lambda c: f"Order Set — {c['pathway_name']}",
     "sections": [("Contents and Deployment", _orderset)]},

    {"name": "Standard Operating Procedure", "count_share": 1.1,
     "id": lambda c: f"SOP-CLIN-{100 + c['idx']:03d}",
     "title": lambda c: f"SOP — {c['pathway_name']} Assessment",
     "sections": [("Procedure", _sop_procedure)]},

    {"name": "Accreditation Evidence Summary", "count_share": 1.0,
     "id": lambda c: f"ACC-{c['idx'] % 60 + 1:03d}",
     "title": lambda c: f"Accreditation Evidence — {c['pathway_name']}",
     "sections": [("Evidence of Compliance", _accred_evidence)]},

    {"name": "Clinical Audit Finding", "count_share": 1.0,
     "id": lambda c: f"CAF-{2024 + c['idx'] % 3}-{c['idx'] % 60 + 1:03d}",
     "title": lambda c: f"Clinical Audit Finding — {c['pathway_name']}",
     "sections": [("Finding and Required Action", _audit_finding)]},

    {"name": "Decision Support Rule Specification", "count_share": 0.9,
     "id": lambda c: f"CDS-{c['idx'] % 50 + 1:03d}",
     "title": lambda c: f"Decision Support Rule — {c['pathway_name']}",
     "sections": [("Trigger and Action", _cds_rule)]},

    {"name": "Clinical Governance Minute", "count_share": 0.8,
     "id": lambda c: f"CGM-{2024 + c['idx'] % 3}-{c['idx'] % 12 + 1:02d}",
     "title": lambda c: f"Governance Minute — {c['pathway_name']} Review",
     "sections": [("Discussion and Decision", _governance)]},
]


def _sp_pathway(rng, i):
    return PATHWAYS[i % len(PATHWAYS)][0]


def _sp_pathway_name(rng, i):
    return PATHWAYS[i % len(PATHWAYS)][1]


def _sp_policy(rng, i):
    return f"CP-POL-{300 + (i % len(PATHWAYS)) * 7:03d}"


PACK = DomainPack(
    key="healthcare_provider",
    spine_fields={"pathway": _sp_pathway, "pathway_name": _sp_pathway_name,
                  "policy": _sp_policy},
    doc_types=DOC_TYPES,
    vocabulary=VOCAB,
    regulations=REGS,
    systems=SYSTEMS,
    roles=ROLES,
    question_seeds=QUESTIONS,
)
