"""Healthcare payer domain pack — claims and revenue cycle.

The counterpart to pack_healthcare_provider.py, and the proof of the subtype
rule. Put the two tenants side by side and the divergence is immediate:

    provider          pathways, order sets, SNOMED/LOINC, accreditation standards,
                      Conditions of Participation, the electronic health record
    payer (here)      medical policy, coverage determination, denial and appeal,
                      CPT/HCPCS and MS-DRG, X12 transaction sets, adjudication

Not one document type, code system, regulator or question is shared. A team that
configures "healthcare" once and reuses it will get one of these two badly wrong.

THE SPINE: medical policy number + procedure code. A claims operations lead
navigates by the policy that decided the outcome and the code that was billed.
The denial notice, the appeal determination, the companion guide and the policy
must all name the same pair.
"""
from .engine import DomainPack

REGS = [
    ("45 CFR 147.136", "internal claims and appeals and external review processes"),
    ("45 CFR 164.502", "uses and disclosures of protected health information"),
    ("42 CFR 422.566", "organisation determinations and notification requirements"),
    ("42 CFR 422.568", "standard timeframes for organisation determinations"),
    ("42 CFR 405.926", "initial determinations and the appeals process"),
    ("29 CFR 2560.503-1", "claims procedure requirements for benefit plans"),
    ("45 CFR 162.1102", "standards for electronic health care claims transactions"),
    ("45 CFR 162.1602", "standards for remittance advice transactions"),
]

SYSTEMS = [
    "the claims adjudication platform", "the medical policy library",
    "the utilisation management workflow", "the provider portal",
    "the clearinghouse gateway", "the appeals and grievances queue",
    "the edit and audit rules engine", "the enrolment and eligibility system",
]

ROLES = [
    "VP Claims Operations", "Medical Policy Director", "Utilisation Management Lead",
    "Appeals and Grievances Manager", "Provider Network Director",
    "Payment Integrity Lead", "Configuration Analyst", "Compliance Officer",
    "Clinical Reviewer", "Revenue Integrity Manager",
]

POLICIES = [
    ("MP-0142", "Advanced Imaging for Low Back Pain", "72148"),
    ("MP-0217", "Continuous Glucose Monitoring", "95250"),
    ("MP-0308", "Sleep Studies and Home Testing", "95810"),
    ("MP-0455", "Bariatric Surgery", "43644"),
    ("MP-0512", "Genetic Testing for Hereditary Cancer", "81162"),
    ("MP-0631", "Spinal Fusion for Degenerative Disease", "22633"),
    ("MP-0704", "Injectable Biologic Therapy", "J3380"),
    ("MP-0819", "Durable Medical Equipment — Mobility", "K0823"),
    ("MP-0925", "Cardiac Rhythm Monitoring", "93298"),
    ("MP-1033", "Physical Therapy Visit Limits", "97110"),
    ("MP-1148", "Skilled Nursing Facility Admission", "99304"),
    ("MP-1250", "Outpatient Infusion Site of Care", "96365"),
]

VOCAB = {
    "denial_reason": [
        "the documentation submitted did not establish that conservative therapy was attempted",
        "the service was performed at a site of care not covered under the benefit",
        "the requested frequency exceeds the limit stated in the policy",
        "prior authorisation was not obtained before the service was rendered",
        "the diagnosis submitted does not support medical necessity for the procedure billed",
        "the member was not eligible on the date of service",
    ],
    "criterion": [
        "documented failure of at least six weeks of conservative management",
        "a documented clinical assessment within the preceding 90 days",
        "the absence of a contraindication recorded in the submitted notes",
        "evidence that a lower cost site of care was considered and excluded",
        "the ordering provider holding the required specialty designation",
    ],
    "timeframe": [
        "within 30 calendar days of receipt for a pre-service request",
        "within 60 calendar days of receipt for a post-service request",
        "within 72 hours for an expedited request",
        "within 15 calendar days where an extension has been applied and notified",
    ],
    "measure": [
        "the first-pass adjudication rate for claims in this policy family",
        "the overturn rate at first-level appeal",
        "the median days from receipt to determination",
        "the proportion of denials citing insufficient documentation",
    ],
}

QUESTIONS = [
    "Why was the claim for procedure code {code_hint} denied?",
    "What are the medical necessity criteria for advanced imaging?",
    "How long do we have to issue a determination on a pre-service request?",
    "Which medical policy governs continuous glucose monitoring?",
    "What documentation is required to overturn this denial on appeal?",
    "Which transaction set carries the remittance advice?",
    "What is the appeal timeframe for a post-service determination?",
    "Does this policy require prior authorisation?",
    "What is the overturn rate at first-level appeal for this policy?",
    "Which site of care is covered for outpatient infusion?",
    "What edit caused this claim to suspend?",
    "Who is authorised to approve a medical policy revision?",
]


def _policy_criteria(ctx):
    return (
        f"{ctx['tenant']} covers {ctx['policy_name']} when the criteria in this policy "
        f"({ctx['policy']}) are met. The primary procedure code addressed by this policy "
        f"is {ctx['code']}.\n\n"
        f"The service is considered medically necessary when the submitted documentation "
        f"establishes {ctx['criterion']}.\n\n"
        f"Where the criteria are not met, the request is denied on the basis that "
        f"{ctx['denial_reason']}. The determination is issued {ctx['timeframe']}."
    )


def _policy_admin(ctx):
    return (
        f"This policy is owned by the {ctx['role']} and reviewed at least annually, or "
        f"sooner where clinical evidence, coding or regulation changes.\n\n"
        f"Revisions are approved by the {ctx['approver']} and configured in "
        f"{ctx['system']}. Configuration is validated against a regression set before "
        f"release to production.\n\n"
        f"Regulatory basis: {ctx['reg'][0]} — {ctx['reg'][1]}."
    )


def _coverage_det(ctx):
    return (
        f"Determination issued under medical policy {ctx['policy']} "
        f"({ctx['policy_name']}) for procedure code {ctx['code']}.\n\n"
        f"Adjudicated against edit {ctx['ref']('Adjudication Edit Specification')} using the "
        f"criteria in {ctx['ref']('Utilisation Management Criteria')}.\n\n"
        f"Outcome: adverse determination. The clinical information submitted did not "
        f"establish {ctx['criterion']}. Specifically, {ctx['denial_reason']}.\n\n"
        f"The determination was issued {ctx['timeframe']} in accordance with "
        f"{ctx['reg'][0]}.\n\n"
        f"The requesting provider and the member have been notified of appeal rights, "
        f"including the information required to support a reconsideration."
    )


def _denial_notice(ctx):
    return (
        f"This notice concerns a claim submitted for procedure code {ctx['code']}, "
        f"adjudicated against medical policy {ctx['policy']} ({ctx['policy_name']}).\n\n"
        f"Determination reference: {ctx['ref']('Coverage Determination')}.\n\n"
        f"Reason for denial: {ctx['denial_reason']}.\n\n"
        f"To request reconsideration, submit documentation evidencing {ctx['criterion']} "
        f"through {ctx['system']}. Requests are accepted {ctx['timeframe']}.\n\n"
        f"Your appeal rights are described under {ctx['reg'][0]} — {ctx['reg'][1]}."
    )


def _appeal_det(ctx):
    return (
        f"First-level appeal determination for a claim adjudicated under medical policy "
        f"{ctx['policy']} ({ctx['policy_name']}), procedure code {ctx['code']}.\n\n"
        f"Reconsidering denial {ctx['ref']('Denial Notice')}. The original denial cited that "
        f"{ctx['denial_reason']}. On reconsideration, the "
        f"clinical reviewer assessed whether the additional documentation establishes "
        f"{ctx['criterion']}.\n\n"
        f"Determination: the original decision is upheld. The submitted records do not "
        f"alter the finding against the policy criteria.\n\n"
        f"The member retains the right to a further level of review as described under "
        f"{ctx['reg'][0]}."
    )


def _companion(ctx):
    return (
        f"This companion guide describes {ctx['tenant']} requirements for electronic "
        f"submission of claims subject to medical policy {ctx['policy']}.\n\n"
        f"Claims for procedure code {ctx['code']} must be submitted using the professional "
        f"or institutional claim transaction as applicable. Remittance is returned on the "
        f"corresponding remittance advice transaction.\n\n"
        f"Eligibility should be verified using the eligibility inquiry and response "
        f"transaction pair before the service is rendered; a claim submitted for an "
        f"ineligible member will deny.\n\n"
        f"Transaction standards are adopted under {ctx['reg'][0]}. Submissions that fail "
        f"structural validation are rejected at {ctx['system']} before adjudication."
    )


def _edit_spec(ctx):
    return (
        f"Adjudication edit supporting medical policy {ctx['policy']} "
        f"({ctx['policy_name']}).\n\n"
        f"Implements medical policy {ctx['policy']} in adjudication.\n\n"
        f"Trigger: a claim line containing procedure code {ctx['code']} where the "
        f"submitted documentation or authorisation record does not evidence "
        f"{ctx['criterion']}.\n\n"
        f"Disposition: suspend the line for clinical review. On review, if "
        f"{ctx['denial_reason']}, the line denies with the corresponding remark code.\n\n"
        f"Configured in {ctx['system']} by the {ctx['role']}. Edit performance is "
        f"monitored through {ctx['measure']}."
    )


def _um_criteria(ctx):
    return (
        f"Utilisation management criteria applied to requests under medical policy "
        f"{ctx['policy']} ({ctx['policy_name']}), procedure code {ctx['code']}.\n\n"
        f"Approve where the submitted documentation establishes {ctx['criterion']}.\n\n"
        f"Refer to clinical review where the documentation is incomplete. Deny where "
        f"{ctx['denial_reason']}.\n\n"
        f"Determinations must be issued {ctx['timeframe']} in accordance with "
        f"{ctx['reg'][0]}."
    )


def _payment_integrity(ctx):
    return (
        f"Payment integrity review of claims adjudicated under medical policy "
        f"{ctx['policy']} ({ctx['policy_name']}).\n\n"
        f"Observation: a proportion of paid claims for procedure code {ctx['code']} lack "
        f"documentation evidencing {ctx['criterion']} on retrospective sampling.\n\n"
        f"Reported measure: {ctx['measure']}.\n\n"
        f"Recommended action: tighten the edit configuration in {ctx['system']} and issue "
        f"provider education. Owner: {ctx['role']}; oversight by the {ctx['approver']}."
    )


DOC_TYPES = [
    {"name": "Medical Policy", "count_share": 1.5,
     "id": lambda c: c["policy"],
     "title": lambda c: f"Medical Policy — {c['policy_name']}",
     "sections": [("Coverage Criteria", _policy_criteria),
                  ("Administration and Review", _policy_admin)]},

    {"name": "Coverage Determination", "count_share": 1.3,
     "id": lambda c: f"CD-{2024 + c['idx'] % 3}-{4000 + c['idx']:05d}",
     "title": lambda c: f"Coverage Determination — {c['policy_name']} ({c['code']})",
     "sections": [("Determination and Rationale", _coverage_det)]},

    {"name": "Denial Notice", "count_share": 1.2,
     "id": lambda c: f"DN-{2024 + c['idx'] % 3}-{7000 + c['idx']:05d}",
     "title": lambda c: f"Denial Notice — Procedure {c['code']} — {c['policy']}",
     "sections": [("Reason and Appeal Rights", _denial_notice)]},

    {"name": "Appeal Determination", "count_share": 1.1,
     "id": lambda c: f"AP1-{2024 + c['idx'] % 3}-{2000 + c['idx']:05d}",
     "title": lambda c: f"Appeal Determination — {c['policy_name']} ({c['code']})",
     "sections": [("Reconsideration Outcome", _appeal_det)]},

    {"name": "EDI Companion Guide Section", "count_share": 0.9,
     "id": lambda c: f"CG-{c['policy'].split('-')[1]}",
     "title": lambda c: f"Companion Guide — Claim Submission for {c['policy_name']}",
     "sections": [("Submission Requirements", _companion)]},

    {"name": "Adjudication Edit Specification", "count_share": 1.1,
     "id": lambda c: f"EDIT-{c['code']}-{c['idx'] % 40:02d}",
     "title": lambda c: f"Adjudication Edit — {c['policy_name']} ({c['code']})",
     "sections": [("Trigger and Disposition", _edit_spec)]},

    {"name": "Utilisation Management Criteria", "count_share": 1.0,
     "id": lambda c: f"UM-{c['policy'].split('-')[1]}-{c['idx'] % 30:02d}",
     "title": lambda c: f"UM Criteria — {c['policy_name']}",
     "sections": [("Review Criteria", _um_criteria)]},

    {"name": "Payment Integrity Review", "count_share": 0.8,
     "id": lambda c: f"PIR-{2024 + c['idx'] % 3}-{c['idx'] % 40 + 1:03d}",
     "title": lambda c: f"Payment Integrity Review — {c['policy_name']}",
     "sections": [("Findings and Recommendation", _payment_integrity)]},
]


def _sp_policy(rng, i):
    return POLICIES[i % len(POLICIES)][0]


def _sp_policy_name(rng, i):
    return POLICIES[i % len(POLICIES)][1]


def _sp_code(rng, i):
    return POLICIES[i % len(POLICIES)][2]


PACK = DomainPack(
    key="healthcare_payer",
    spine_fields={"policy": _sp_policy, "policy_name": _sp_policy_name, "code": _sp_code},
    doc_types=DOC_TYPES,
    vocabulary=VOCAB,
    regulations=REGS,
    systems=SYSTEMS,
    roles=ROLES,
    question_seeds=QUESTIONS,
)
