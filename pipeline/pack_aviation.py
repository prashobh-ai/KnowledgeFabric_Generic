"""Aviation domain pack — operator (continuing airworthiness) and MRO.

Terminology, document names and regulatory citations follow public sources:
14 CFR Parts 39/43/91/121/145, EASA Part-145/Part-M/Part-CAMO under Regulation
(EU) No 1321/2014, ATA iSpec 2200 chapter numbering, and S1000D. The content is
invented; the shape is not.

THE SPINE: aircraft registration + ATA chapter. A continuing-airworthiness
engineer navigates by exactly these two. An Airworthiness Directive names an
applicability; a task card closes it against a tail; a technical log records the
defect that triggered it. The same registration must appear in all three or the
knowledge graph has nothing genuine to link.
"""
from .engine import DomainPack

REGS = [
    ("14 CFR 39.7", "operating a product that does not comply with an applicable AD"),
    ("14 CFR 39.15", "an AD continues to apply after a product is modified or repaired"),
    ("14 CFR 43.9", "content, form and disposition of maintenance records"),
    ("14 CFR 91.403", "the owner or operator is primarily responsible for airworthiness"),
    ("14 CFR 91.417", "maintenance records retention"),
    ("14 CFR 121.367", "maintenance, preventive maintenance and alterations programme"),
    ("14 CFR 145.109", "repair station equipment, materials and data requirements"),
    ("14 CFR 145.219", "repair station recordkeeping"),
    ("EASA Part-145 145.A.50", "certification of maintenance and release to service"),
    ("EASA Part-M M.A.301", "continuing airworthiness tasks"),
    ("EASA Part-CAMO CAMO.A.315", "continuing airworthiness management"),
]

SYSTEMS = [
    "the maintenance information system", "the electronic technical log",
    "the airworthiness compliance register", "the planning and forecasting module",
    "the parts and inventory system", "the reliability reporting database",
    "the flight operations documentation portal", "the safety reporting system",
]

ROLES = [
    "Continuing Airworthiness Manager", "Quality Manager", "Base Maintenance Planner",
    "Certifying Staff (B1)", "Certifying Staff (B2)", "Reliability Engineer",
    "Technical Records Controller", "Head of Airworthiness Review",
    "Line Maintenance Supervisor", "Design Liaison Engineer",
]

ATA = [
    ("21", "Air Conditioning"), ("22", "Auto Flight"), ("23", "Communications"),
    ("24", "Electrical Power"), ("25", "Equipment and Furnishings"),
    ("27", "Flight Controls"), ("28", "Fuel"), ("29", "Hydraulic Power"),
    ("32", "Landing Gear"), ("34", "Navigation"), ("36", "Pneumatic"),
    ("49", "Airborne Auxiliary Power"), ("52", "Doors"), ("57", "Wings"),
    ("71", "Power Plant"), ("73", "Engine Fuel and Control"),
]

FLEET = ["QA-320N", "QA-321N", "QA-737M", "QA-738M", "QA-350K", "QA-787J", "QA-E90R"]

VOCAB = {
    "finding": [
        "corrosion beyond allowable limits at the fastener row",
        "chafing of the harness against a structural former",
        "an out-of-tolerance actuator response time",
        "moisture ingress at the connector backshell",
        "delamination detected during tap inspection",
        "a repeat defect recorded on three consecutive sectors",
        "an unapproved repair scheme found during records review",
    ],
    "action": [
        "accomplish the inspection at or before the next A-check",
        "replace the affected component with a serviceable unit",
        "apply the approved repair scheme and record the deviation",
        "carry out a repetitive inspection at the stated interval",
        "raise an Engineering Order and defer under the applicable relief",
        "quarantine the part and raise a technical query with the design organisation",
    ],
    "interval": [
        "500 flight hours or 300 cycles, whichever occurs first",
        "750 flight hours",
        "12 calendar months",
        "1,000 flight cycles",
        "each transit check until terminating action is embodied",
    ],
    "condition": [
        "the aircraft is released to service under the applicable relief",
        "no further defect is recorded against the same system",
        "the deferred item remains within the permitted rectification interval",
        "the repetitive inspection continues at the stated interval",
    ],
}

QUESTIONS = [
    "Which airworthiness directives are open against {reg_hint}?",
    "What is the repetitive inspection interval for the {ata_hint} inspection?",
    "Can we defer this defect and for how long?",
    "Which task card closes the AD compliance for the landing gear?",
    "What repair scheme was approved for the fuselage corrosion finding?",
    "Who is authorised to release the aircraft to service after this work?",
    "What records must we retain for this maintenance action?",
    "Which regulation makes the operator responsible for airworthiness?",
    "What triggered the repeat defect on the hydraulic system?",
    "Has the terminating action been embodied on the fleet?",
    "What is the ATA chapter for the pneumatic system?",
    "Which service bulletin does this engineering order implement?",
]


def _ad(ctx):
    return (
        f"This directive is issued in response to reports of {ctx['finding']} affecting "
        f"the {ctx['ata_name']} system (ATA Chapter {ctx['ata']}) on aircraft of the type "
        f"operated by {ctx['tenant']}. The unsafe condition, if not addressed, could "
        f"result in degraded system function during flight.\n\n"
        f"Applicability extends to the aircraft identified by registration {ctx['tail']} "
        f"and to all aircraft of the same type and configuration within the fleet.\n\n"
        f"Required action: {ctx['action']}. The compliance time is {ctx['interval']} "
        f"from the effective date of this directive.\n\n"
        f"Under {ctx['reg'][0]}, {ctx['reg'][1]}. Operators must record accomplishment "
        f"in {ctx['system']} before further flight."
    )


def _ad_effect(ctx):
    return (
        f"No alternative method of compliance has been approved at the date of issue. "
        f"Requests for an alternative method must be submitted with supporting data "
        f"through the {ctx['approver']}.\n\n"
        f"Accomplishment must be recorded against registration {ctx['tail']} in "
        f"{ctx['system']}, cross-referenced to task card {ctx['ref']('Maintenance Task Card')} "
        f"raised to perform the work. Where a service bulletin provides the terminating "
        f"action, refer to {ctx['ref']('Service Bulletin')}."
    )


def _task_purpose(ctx):
    return (
        f"This task card provides the instructions necessary to {ctx['action']} on the "
        f"{ctx['ata_name']} system (ATA Chapter {ctx['ata']}) of aircraft {ctx['tail']}.\n\n"
        f"The task is raised to satisfy the compliance requirement recorded in "
        f"{ctx['ref']('Airworthiness Directive Compliance Record')} and is referenced by "
        f"engineering order {ctx['ref']('Engineering Order')}. Work must not commence "
        f"until the applicable maintenance data has been confirmed as current in "
        f"{ctx['system']}."
    )


def _task_steps(ctx):
    r = ctx["rng"]
    steps = [
        "Confirm the aircraft is electrically safe and access panels are removed in accordance with the maintenance manual.",
        f"Inspect the {ctx['ata_name'].lower()} installation for {ctx['finding']}.",
        "Record all measurements on the worksheet. Any measurement outside the stated limits requires a technical query.",
        f"{ctx['action'].capitalize()}.",
        "Restore access, carry out an operational test, and confirm no leakage or abnormal indication.",
        "Complete the certification block and enter the work against the aircraft record.",
    ]
    r.shuffle(steps[1:4])
    return "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps))


def _task_cert(ctx):
    return (
        f"Certification of this task constitutes a release to service for the work "
        f"performed. Under {ctx['reg'][0]}, {ctx['reg'][1]}.\n\n"
        f"Only {ctx['role']} holding the appropriate category authorisation may certify "
        f"this task. The certifying signature must be accompanied by the authorisation "
        f"number and the date of completion, recorded in {ctx['system']}."
    )


def _mel_relief(ctx):
    return (
        f"This entry permits dispatch of aircraft {ctx['tail']} with the "
        f"{ctx['ata_name']} item inoperative, subject to the conditions stated below.\n\n"
        f"Rectification interval: Category C — 10 consecutive calendar days, "
        f"excluding the day the defect was recorded.\n\n"
        f"Dispatch is permitted provided {ctx['condition']}. Rectification is tracked "
        f"through {ctx['ref']('Engineering Order')}. If the condition ceases to "
        f"be met, the relief is void and the aircraft must not be dispatched until the "
        f"defect is rectified."
    )


def _mel_proc(ctx):
    return (
        f"Maintenance procedure: isolate the affected {ctx['ata_name'].lower()} circuit, "
        f"secure the control in the safe position, and placard the affected control in "
        f"the flight deck.\n\n"
        f"Operations procedure: the commander must be advised of the inoperative item "
        f"before departure. Performance penalties, where applicable, are applied through "
        f"the dispatch calculation.\n\n"
        f"The deferred item must be visible in {ctx['system']} and reviewed at each "
        f"transit until closed."
    )


def _log_entry(ctx):
    return (
        f"Defect reported by the operating crew on aircraft {ctx['tail']}: "
        f"{ctx['finding']} associated with the {ctx['ata_name']} system "
        f"(ATA Chapter {ctx['ata']}).\n\n"
        f"Initial assessment by {ctx['role']} confirmed the reported condition. "
        f"The defect was deferred under the applicable relief and an engineering order "
        f"{ctx['ref']('Engineering Order')} was raised to {ctx['action']}.\n\n"
        f"Deferral applied under {ctx['ref']('Minimum Equipment List Entry')}. The entry "
        f"remains open in {ctx['system']} and is reviewed at each transit check."
    )


def _sb_summary(ctx):
    return (
        f"This service bulletin introduces a modification to the {ctx['ata_name']} "
        f"system (ATA Chapter {ctx['ata']}) to address {ctx['finding']}.\n\n"
        f"Compliance is recommended at {ctx['interval']}. Where an airworthiness "
        f"directive mandates this bulletin, the directive compliance time takes "
        f"precedence.\n\n"
        f"Embodiment on aircraft {ctx['tail']} is planned during the next scheduled "
        f"input and is managed through engineering order {ctx['ref']('Engineering Order')}. "
        f"Where mandated, see {ctx['ref']('Airworthiness Directive Compliance Record')}."
    )


def _eo_scope(ctx):
    return (
        f"This engineering order authorises the work necessary to {ctx['action']} on "
        f"aircraft {ctx['tail']}, {ctx['ata_name']} system, ATA Chapter {ctx['ata']}.\n\n"
        f"The order implements service bulletin {ctx['ref']('Service Bulletin')} and "
        f"satisfies the requirement recorded in "
        f"{ctx['ref']('Airworthiness Directive Compliance Record')}. It is executed "
        f"through task card {ctx['ref']('Maintenance Task Card')}. Approved data is held in "
        f"{ctx['system']} and must be verified as current before work begins.\n\n"
        f"Man-hour estimate and material requirements are attached to the work package "
        f"raised in {ctx['system_2']}."
    )


def _moe_scope(ctx):
    return (
        f"{ctx['tenant']} maintains an approved maintenance organisation exposition "
        f"describing the scope of work, facilities, personnel and procedures under which "
        f"maintenance is performed.\n\n"
        f"The organisation holds capability for the {ctx['ata_name']} system "
        f"(ATA Chapter {ctx['ata']}) at base and line level. Work outside the stated "
        f"capability requires a subcontract arrangement approved by the {ctx['approver']}.\n\n"
        f"Under {ctx['reg'][0]}, {ctx['reg'][1]}."
    )


def _rel_summary(ctx):
    return (
        f"During the reporting period the {ctx['ata_name']} system (ATA Chapter "
        f"{ctx['ata']}) recorded an elevated defect rate across the fleet, with "
        f"aircraft {ctx['tail']} accounting for a disproportionate share.\n\n"
        f"The dominant reported condition was {ctx['finding']}. Analysis indicates the "
        f"condition is associated with a specific production batch rather than an "
        f"operational cause. Related directive: "
        f"{ctx['ref']('Airworthiness Directive Compliance Record')}.\n\n"
        f"Recommended action: {ctx['action']}, and monitor the affected population at "
        f"{ctx['interval']}."
    )


def _audit(ctx):
    return (
        f"Finding raised during the internal quality audit of the maintenance "
        f"organisation. Evidence sampled against aircraft {ctx['tail']}, "
        f"{ctx['ata_name']} system.\n\n"
        f"Observation: {ctx['finding']} was recorded on task card "
        f"{ctx['ref']('Maintenance Task Card')} without the corresponding technical query "
        f"being raised, contrary to {ctx['ref']('Maintenance Organisation Exposition Section')}.\n\n"
        f"Regulatory reference: {ctx['reg'][0]} — {ctx['reg'][1]}.\n\n"
        f"Corrective action required: {ctx['action']}. Response due within 30 days to "
        f"the {ctx['approver']}."
    )


DOC_TYPES = [
    {"name": "Airworthiness Directive Compliance Record", "count_share": 1.4,
     "id": lambda c: f"ADCR-{2024 + c['idx'] % 3}-{100 + c['idx']:04d}",
     "title": lambda c: f"AD Compliance Record — {c['ata_name']} (ATA {c['ata']}) — {c['tail']}",
     "sections": [("Unsafe Condition and Required Action", _ad),
                  ("Alternative Methods and Recording", _ad_effect)]},

    {"name": "Maintenance Task Card", "count_share": 1.8,
     "id": lambda c: f"TC-{c['ata']}-{200 + c['idx']:04d}",
     "title": lambda c: f"Task Card — {c['ata_name']} Inspection — {c['tail']}",
     "sections": [("Purpose and Applicability", _task_purpose),
                  ("Procedure", _task_steps),
                  ("Certification and Release", _task_cert)]},

    {"name": "Minimum Equipment List Entry", "count_share": 1.0,
     "id": lambda c: f"MEL-{c['ata']}-{c['idx'] % 900:03d}",
     "title": lambda c: f"MEL Entry — {c['ata_name']} — ATA {c['ata']}",
     "sections": [("Relief and Conditions", _mel_relief),
                  ("Maintenance and Operations Procedures", _mel_proc)]},

    {"name": "Technical Log Entry", "count_share": 1.5,
     "id": lambda c: f"TLE-{c['tail'][-4:]}-{500 + c['idx']:04d}",
     "title": lambda c: f"Technical Log Entry — {c['tail']} — {c['ata_name']}",
     "sections": [("Defect and Rectification", _log_entry)]},

    {"name": "Service Bulletin", "count_share": 0.9,
     "id": lambda c: f"SB-{c['ata']}-{c['idx'] % 900 + 10:03d}",
     "title": lambda c: f"Service Bulletin — {c['ata_name']} Modification",
     "sections": [("Planning Information", _sb_summary)]},

    {"name": "Engineering Order", "count_share": 1.1,
     "id": lambda c: f"EO-{2024 + c['idx'] % 3}-{300 + c['idx']:04d}",
     "title": lambda c: f"Engineering Order — {c['ata_name']} — {c['tail']}",
     "sections": [("Scope and Authorisation", _eo_scope)]},

    {"name": "Maintenance Organisation Exposition Section", "count_share": 0.6,
     "id": lambda c: f"MOE-{c['idx'] % 900 + 1:03d}",
     "title": lambda c: f"Maintenance Organisation Exposition — Capability, ATA {c['ata']}",
     "sections": [("Scope of Approval", _moe_scope)]},

    {"name": "Reliability Report", "count_share": 0.8,
     # Must include the sequence, not only cycling values — otherwise two
     # tenants sharing this pack collide on the same report numbers.
     "id": lambda c: f"REL-{2024 + c['idx'] % 3}-Q{1 + c['idx'] % 4}-{c['ata']}-{c['idx']:03d}",
     "title": lambda c: f"Reliability Report — {c['ata_name']} — Quarter {1 + c['idx'] % 4}",
     "sections": [("Fleet Performance Summary", _rel_summary)]},

    {"name": "Quality Audit Finding", "count_share": 0.9,
     "id": lambda c: f"QAF-{2024 + c['idx'] % 3}-{c['idx'] % 900 + 1:03d}",
     "title": lambda c: f"Quality Audit Finding — {c['ata_name']} Records — {c['tail']}",
     "sections": [("Finding and Corrective Action", _audit)]},
]


def _spine_ata(rng, i):
    return ATA[i % len(ATA)][0]


def _spine_ata_name(rng, i):
    return ATA[i % len(ATA)][1]


def _spine_tail(rng, i):
    return f"{FLEET[i % len(FLEET)]}"


# Operator and MRO are different subtypes and must not share a corpus shape.
# An operator's world is airworthiness management: directives, deferrals, tech
# logs, reliability. An MRO's world is the shop floor: task cards, engineering
# orders, capability, release certification. Same industry, same ATA numbering,
# genuinely different document mix — so the two tenants are not interchangeable.
PROFILE_WEIGHTS = {
    "operator": {
        "Airworthiness Directive Compliance Record": 1.8,
        "Technical Log Entry": 1.9,
        "Minimum Equipment List Entry": 1.6,
        "Reliability Report": 1.3,
        "Maintenance Task Card": 0.7,
        "Engineering Order": 0.6,
        "Service Bulletin": 0.5,
        "Maintenance Organisation Exposition Section": 0.3,
        "Quality Audit Finding": 0.8,
    },
    "mro": {
        "Maintenance Task Card": 2.2,
        "Engineering Order": 1.8,
        "Maintenance Organisation Exposition Section": 1.4,
        "Service Bulletin": 1.4,
        "Quality Audit Finding": 1.3,
        "Airworthiness Directive Compliance Record": 0.6,
        "Technical Log Entry": 0.4,
        "Minimum Equipment List Entry": 0.2,
        "Reliability Report": 0.5,
    },
}


def for_profile(profile: str) -> DomainPack:
    """Return a pack whose document mix matches the subtype."""
    weights = PROFILE_WEIGHTS.get(profile)
    if not weights:
        return PACK
    tuned = []
    for dt in DOC_TYPES:
        d = dict(dt)
        d["count_share"] = weights.get(dt["name"], dt.get("count_share", 1.0))
        tuned.append(d)
    return DomainPack(
        key=f"aviation_{profile}", spine_fields=PACK.spine_fields, doc_types=tuned,
        vocabulary=VOCAB, regulations=REGS, systems=SYSTEMS, roles=ROLES,
        question_seeds=QUESTIONS,
    )


PACK = DomainPack(
    key="aviation",
    spine_fields={"tail": _spine_tail, "ata": _spine_ata, "ata_name": _spine_ata_name},
    doc_types=DOC_TYPES,
    vocabulary=VOCAB,
    regulations=REGS,
    systems=SYSTEMS,
    roles=ROLES,
    question_seeds=QUESTIONS,
)
