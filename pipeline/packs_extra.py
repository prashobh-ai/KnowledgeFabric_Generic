"""Remaining domain packs.

Kept in one module because packs are DATA, not logic — the engine and the three
reference packs (aviation, healthcare provider, healthcare payer) establish the
pattern, and these follow it. Splitting seven small data files across seven
modules would add navigation cost without adding clarity.

Each pack declares its own spine, the identifiers a practitioner in that subtype
actually navigates by:

    pharma      study identifier + SOP number
    devices     device model + clearance reference
    banking     regulatory obligation + internal control
    insurance   policy form number + coverage section
    maritime    vessel + equipment tag
    retail      article number + vendor identifier
    quality     requirement identifier + test suite

Terminology and citations follow public standards and regulator sources. All
content is invented.
"""
from .engine import DomainPack


def _pack(key, spine_defs, doc_defs, vocab, regs, systems, roles, questions):
    """Compact constructor. spine_defs: {field: [values]} indexed positionally."""
    fields = {}
    for name, values in spine_defs.items():
        fields[name] = (lambda vals: (lambda rng, i: vals[i % len(vals)]))(values)
    return DomainPack(key=key, spine_fields=fields, doc_types=doc_defs,
                      vocabulary=vocab, regulations=regs, systems=systems,
                      roles=roles, question_seeds=questions)


def _sec(text_fn):
    return text_fn


# ============================================================ PHARMA / GxP
_PH_STUDIES = ["QP-2401-ONC", "QP-2402-CNS", "QP-2403-CVM", "QP-2404-IMM",
               "QP-2405-RES", "QP-2406-MET", "QP-2407-DER", "QP-2408-HEM",
               "QP-2409-INF", "QP-2410-NEP"]
_PH_NAMES = ["Phase II Oncology Dose Expansion", "Phase I CNS Safety and Tolerability",
             "Phase III Cardiovascular Outcomes", "Phase II Immunology Efficacy",
             "Phase II Respiratory Exacerbation", "Phase III Metabolic Control",
             "Phase II Dermatology Lesion Response", "Phase I Haematology Pharmacokinetics",
             "Phase III Infectious Disease Prevention", "Phase II Nephrology Progression"]
_PH_SOPS = [f"SOP-CL-{200 + i * 11:03d}" for i in range(10)]

PHARMA = _pack(
    "pharma",
    {"study": _PH_STUDIES, "study_name": _PH_NAMES, "sop": _PH_SOPS},
    [
        {"name": "Clinical Study Protocol", "count_share": 1.3,
         "id": lambda c: f"{c['study']}-PROT",
         "title": lambda c: f"Clinical Study Protocol — {c['study_name']} ({c['study']})",
         "sections": [("Objectives and Design", lambda c:
            f"This protocol describes the conduct of study {c['study']} "
            f"({c['study_name']}) sponsored by {c['tenant']}.\n\n"
            f"The primary objective is to evaluate {c['endpoint']} in the population "
            f"defined by the eligibility criteria. Subjects are assessed at each visit "
            f"in accordance with the schedule of assessments.\n\n"
            f"Conduct follows {c['reg'][0]} — {c['reg'][1]}. Site-level execution is "
            f"governed by {c['sop']}."),
          ("Data Handling and Oversight", lambda c:
            f"Data are captured in {c['system']} and reconciled against source. "
            f"Any {c['deviation']} is recorded as a protocol deviation and assessed for "
            f"impact on subject safety and data integrity.\n\n"
            f"Oversight rests with the {c['approver']}. Deviations meeting the "
            f"seriousness criteria are escalated within {c['timeframe']}.")]},

        {"name": "Investigator Brochure Section", "count_share": 0.9,
         "id": lambda c: f"{c['study']}-IB",
         "title": lambda c: f"Investigator Brochure — {c['study_name']}",
         "sections": [("Summary of Known Risks", lambda c:
            f"This section summarises the non-clinical and clinical information "
            f"relevant to investigators conducting study {c['study']}.\n\n"
            f"The most frequently reported events are consistent with the mechanism of "
            f"action. Investigators must remain alert to {c['deviation']} and report in "
            f"accordance with {c['sop']}.\n\n"
            f"Reference safety information is maintained current and reissued whenever "
            f"the risk profile changes materially.")]},

        {"name": "Standard Operating Procedure", "count_share": 1.3,
         "id": lambda c: c["sop"],
         "title": lambda c: f"SOP — Study Conduct and Documentation ({c['sop']})",
         "sections": [("Purpose and Scope", lambda c:
            f"This procedure defines how {c['tenant']} personnel conduct and document "
            f"activities for studies including {c['study']}.\n\n"
            f"It applies to all staff performing the activity, regardless of location. "
            f"Compliance is required under {c['reg'][0]} — {c['reg'][1]}."),
          ("Procedure", lambda c:
            f"1. Confirm the current protocol version before performing the activity.\n"
            f"2. Record the activity in {c['system']} at the time it is performed.\n"
            f"3. Where {c['deviation']} occurs, raise a deviation record {c['timeframe']}.\n"
            f"4. Assess the deviation for impact on {c['endpoint']}.\n"
            f"5. Route to the {c['approver']} for classification and CAPA decision.")]},

        {"name": "Protocol Deviation Record", "count_share": 1.2,
         "id": lambda c: f"DEV-{c['study'].split('-')[1]}-{300 + c['idx']:04d}",
         "title": lambda c: f"Protocol Deviation — {c['study']} — {c['study_name']}",
         "sections": [("Description and Impact", lambda c:
            f"Deviation recorded against study {c['study']} ({c['study_name']}).\n\n"
            f"Description: {c['deviation']}, contrary to the protocol for study {c['study']} "
            f"and procedure {c['sop']}. Protocol reference: {c['ref']('Clinical Study Protocol')}.\n\n"
            f"Impact assessment: no impact on subject safety identified. Impact on "
            f"{c['endpoint']} assessed as not significant.\n\n"
            f"Classification and CAPA decision made by the {c['approver']} within "
            f"{c['timeframe']}.")]},

        {"name": "CAPA Record", "count_share": 1.0,
         "id": lambda c: f"CAPA-{2024 + c['idx'] % 3}-{c['idx'] % 60 + 1:03d}",
         "title": lambda c: f"CAPA — {c['study_name']} Deviation Trend",
         "sections": [("Root Cause and Action", lambda c:
            f"Corrective and preventive action arising from repeated deviations on "
            f"study {c['study']}.\n\n"
            f"Arises from deviation {c['ref']('Protocol Deviation Record')} on study {c['study']}.\n\n"
            f"Root cause: procedure {c['sop']} did not state the required action clearly "
            f"enough at the point of use, leading to {c['deviation']}.\n\n"
            f"Corrective action: revise {c['sop']} and retrain affected personnel. "
            f"Preventive action: add a system check in {c['system']}.\n\n"
            f"Effectiveness is verified {c['timeframe']} after implementation.")]},

        {"name": "Clinical Study Report Section", "count_share": 0.9,
         "id": lambda c: f"{c['study']}-CSR",
         "title": lambda c: f"Clinical Study Report — {c['study_name']}",
         "sections": [("Results Summary", lambda c:
            f"Study {c['study']} ({c['study_name']}) completed enrolment and follow-up "
            f"in accordance with the protocol.\n\n"
            f"The analysis of {c['endpoint']} was performed on the defined analysis set. "
            f"Deviations, including instances where {c['deviation']}, were reviewed and "
            f"assessed as not affecting the interpretation of the primary result.\n\n"
            f"Reporting follows {c['reg'][0]}.")]},

        {"name": "Computerised System Validation Summary", "count_share": 0.8,
         "id": lambda c: f"CSV-{c['idx'] % 40 + 1:03d}",
         "title": lambda c: f"Validation Summary — {c['system'].strip('the ').title()}",
         "sections": [("Validation Approach and Outcome", lambda c:
            f"This summary records the validation of {c['system']} supporting study "
            f"{c['study']}.\n\n"
            f"Installation, operational and performance qualification were executed "
            f"against approved protocols. Electronic records and signatures meet the "
            f"requirements of {c['reg'][0]} — {c['reg'][1]}.\n\n"
            f"Audit trail review confirmed that changes are attributable, legible and "
            f"contemporaneous. Periodic review is scheduled {c['timeframe']}.")]},

        {"name": "Trial Master File Index Entry", "count_share": 0.8,
         "id": lambda c: f"TMF-{c['study'].split('-')[1]}-{c['idx'] % 50 + 1:03d}",
         "title": lambda c: f"TMF Index — {c['study_name']} Essential Documents",
         "sections": [("Completeness Status", lambda c:
            f"Essential document inventory for study {c['study']} ({c['study_name']}).\n\n"
            f"The file is maintained contemporaneously in {c['system']}. Documents "
            f"required before site activation are complete; those required during "
            f"conduct are filed {c['timeframe']}.\n\n"
            f"Outstanding items are tracked by the {c['role']} and reported to the "
            f"{c['approver']} ahead of inspection readiness review.")]},
    ],
    {"endpoint": ["the primary efficacy endpoint", "the composite safety endpoint",
                  "the change from baseline in the primary measure",
                  "time to first event", "the pharmacokinetic exposure parameter"],
     "deviation": ["an assessment performed outside the protocol visit window",
                   "informed consent documented on a superseded form version",
                   "a dose administered without the required prior laboratory result",
                   "source data not reconciled to the case report form within the interval",
                   "a temperature excursion in investigational product storage"],
     "timeframe": ["within five working days", "within 24 hours of awareness",
                   "at the next monitoring visit", "within 30 days of classification"]},
    [("21 CFR Part 11", "electronic records and electronic signatures"),
     ("21 CFR 312.60", "general responsibilities of investigators"),
     ("21 CFR 312.62", "investigator recordkeeping and record retention"),
     ("ICH E6(R2) Section 5.0", "sponsor quality management in clinical trials"),
     ("ICH E6(R2) Section 4.9", "investigator records and reports"),
     ("ICH E3", "structure and content of clinical study reports"),
     ("EU Annex 11", "computerised systems in GMP environments")],
    ["the electronic data capture system", "the clinical trial management system",
     "the electronic trial master file", "the safety database",
     "the document management system", "the randomisation and supply system"],
    ["Head of Clinical Quality Assurance", "Clinical Operations Director",
     "Medical Monitor", "Data Management Lead", "Biostatistics Lead",
     "Pharmacovigilance Manager", "Regulatory Affairs Director",
     "Clinical Trial Manager", "Quality Systems Manager"],
    ["Which SOP governs protocol deviation reporting?",
     "What is the impact assessment for this deviation?",
     "Which study does this CAPA relate to?",
     "What are the Part 11 requirements for the data capture system?",
     "How quickly must a serious deviation be escalated?",
     "What is the primary endpoint for the oncology study?",
     "Which essential documents are outstanding in the trial master file?",
     "Who approves a change to the study protocol?",
     "What root cause was identified for the repeated deviations?",
     "How is validation of the clinical system evidenced?"],
)


# ========================================================== MEDICAL DEVICES
_DV_MODELS = ["QM-100 Analyser", "QM-200 Monitor", "QM-310 Infusion Controller",
              "QM-450 Imaging Console", "QM-520 Point-of-Care Meter",
              "QM-610 Ventilator Module", "QM-700 Surgical Navigation Unit",
              "QM-820 Patient Sensor", "QM-905 Diagnostic Cartridge",
              "QM-960 Sterilisation Indicator"]
_DV_CLEAR = [f"K{24}{1000 + i * 137:04d}" for i in range(10)]

DEVICES = _pack(
    "devices",
    {"model": _DV_MODELS, "clearance": _DV_CLEAR},
    [
        {"name": "Instructions for Use", "count_share": 1.3,
         "id": lambda c: f"IFU-{c['model'].split()[0]}",
         "title": lambda c: f"Instructions for Use — {c['model']}",
         "sections": [("Intended Use", lambda c:
            f"The {c['model']} is intended for {c['intended_use']}. It is for use by "
            f"trained healthcare professionals in the settings described in this document.\n\n"
            f"This device was cleared under {c['clearance']}. Use outside the stated "
            f"intended use has not been evaluated.\n\n"
            f"Manufactured by {c['tenant']}."),
          ("Warnings and Limitations", lambda c:
            f"Do not use the device if {c['hazard']} is present or suspected.\n\n"
            f"Results may be affected by {c['interference']}. Where this is suspected, "
            f"confirm by an alternative method before acting on the result.\n\n"
            f"Report any {c['complaint']} to {c['tenant']} and, where applicable, to the "
            f"competent authority under {c['reg'][0]}.")]},

        {"name": "510(k) Summary", "count_share": 1.0,
         "id": lambda c: c["clearance"],
         "title": lambda c: f"510(k) Summary — {c['model']} ({c['clearance']})",
         "sections": [("Substantial Equivalence", lambda c:
            f"The {c['model']} is substantially equivalent to the identified predicate "
            f"device in intended use, technological characteristics and performance.\n\n"
            f"Intended use: {c['intended_use']}.\n\n"
            f"Performance testing addressed accuracy, precision, and the effect of "
            f"{c['interference']}. Results support a determination of substantial "
            f"equivalence.\n\n"
            f"Regulatory basis: {c['reg'][0]} — {c['reg'][1]}.")]},

        {"name": "Design History File Record", "count_share": 1.1,
         "id": lambda c: f"DHF-{c['model'].split()[0]}-{c['idx'] % 40 + 1:03d}",
         "title": lambda c: f"Design History File — {c['model']} Design Control",
         "sections": [("Design Input and Verification", lambda c:
            f"Design control record for the {c['model']}, cleared under {c['clearance']}.\n\n"
            f"Design input: the device shall perform {c['intended_use']} within the stated "
            f"accuracy across the specified operating range.\n\n"
            f"Verification confirmed that the requirement is met, including under "
            f"{c['interference']}. Validation confirmed the device meets user needs in "
            f"the intended environment.\n\n"
            f"Maintained under {c['reg'][0]} — {c['reg'][1]}.")]},

        {"name": "Risk Management File Entry", "count_share": 1.0,
         "id": lambda c: f"RMF-{c['model'].split()[0]}-{c['idx'] % 40 + 1:03d}",
         "title": lambda c: f"Risk Management — {c['model']} Hazard Analysis",
         "sections": [("Hazard, Control and Residual Risk", lambda c:
            f"Hazard analysis entry for the {c['model']}.\n\n"
            f"Hazard: {c['hazard']}. Foreseeable sequence of events: the condition is "
            f"not detected, and a result is acted upon that does not reflect the true "
            f"value.\n\n"
            f"Risk control: the design detects and flags the condition; the instructions "
            f"for use state the limitation explicitly.\n\n"
            f"Residual risk is judged acceptable against the benefit of "
            f"{c['intended_use']}. Verified through the design verification record.")]},

        {"name": "Complaint Record", "count_share": 1.2,
         "id": lambda c: f"CMP-{2024 + c['idx'] % 3}-{5000 + c['idx']:05d}",
         "title": lambda c: f"Complaint Record — {c['model']}",
         "sections": [("Complaint and Investigation", lambda c:
            f"Complaint received concerning the {c['model']} (cleared under "
            f"{c['clearance']}).\n\n"
            f"Reported condition: {c['complaint']}.\n\n"
            f"Design reference: {c['ref']('Design History File Record')}; risk entry "
            f"{c['ref']('Risk Management File Entry')}.\n\n"
            f"Investigation: the returned unit was examined against the design specification. The reported condition is consistent with {c['interference']} "
            f"rather than a device malfunction.\n\n"
            f"Reportability decision: assessed against {c['reg'][0]} and determined not "
            f"reportable. Decision recorded by the {c['approver']}.")]},

        {"name": "CAPA Record", "count_share": 0.9,
         "id": lambda c: f"CAPA-DEV-{c['idx'] % 50 + 1:03d}",
         "title": lambda c: f"CAPA — {c['model']} Complaint Trend",
         "sections": [("Root Cause and Action", lambda c:
            f"CAPA raised on complaint {c['ref']('Complaint Record')} and a trend of reports of "
            f"{c['complaint']} for the {c['model']} (cleared under {c['clearance']}).\n\n"
            f"Root cause: the instructions for use did not state the limitation "
            f"concerning {c['interference']} prominently enough at the point of use.\n\n"
            f"Corrective action: revise the instructions for use and issue a customer "
            f"notification. Preventive action: add the limitation to the design review "
            f"checklist.\n\n"
            f"Effectiveness verified through complaint rate monitoring.")]},

        {"name": "Quality Management Procedure", "count_share": 0.9,
         "id": lambda c: f"QMP-{c['idx'] % 40 + 100:03d}",
         "title": lambda c: f"Quality Procedure — Complaint Handling and Reporting",
         "sections": [("Procedure", lambda c:
            f"1. Record every complaint concerning devices including the {c['model']} on "
            f"receipt, in {c['system']}.\n"
            f"2. Determine whether the complaint concerns a device malfunction or "
            f"{c['interference']}.\n"
            f"3. Assess reportability against {c['reg'][0]}.\n"
            f"4. Where reportable, submit within the required timeframe.\n"
            f"5. Trend complaints; where a trend emerges, raise a CAPA.\n\n"
            f"Owner: {c['role']}. Oversight: {c['approver']}.")]},

        {"name": "Post-Market Surveillance Report", "count_share": 0.8,
         "id": lambda c: f"PMS-{2024 + c['idx'] % 3}-{c['model'].split()[0]}",
         "title": lambda c: f"Post-Market Surveillance — {c['model']}",
         "sections": [("Surveillance Findings", lambda c:
            f"Surveillance summary for the {c['model']}, cleared under {c['clearance']}.\n\n"
            f"Complaint volume for the period was consistent with the installed base. The "
            f"most frequently reported condition was {c['complaint']}, predominantly "
            f"associated with {c['interference']}.\n\n"
            f"No new hazard was identified. The risk management file remains valid and "
            f"the benefit-risk determination is unchanged.")]},
    ],
    {"intended_use": ["quantitative measurement of the target analyte in whole blood",
                      "continuous monitoring of the physiological parameter in acute settings",
                      "controlled delivery of the prescribed therapy",
                      "visualisation and review of acquired diagnostic images",
                      "point-of-care determination for professional use"],
     "hazard": ["an out-of-range ambient temperature", "an expired or damaged consumable",
                "an incompletely seated cartridge", "an interfering substance in the sample",
                "electromagnetic interference from adjacent equipment"],
     "interference": ["an interfering substance above the stated concentration",
                      "sample handling outside the stated conditions",
                      "operation outside the specified temperature range",
                      "use of a consumable beyond its expiry"],
     "complaint": ["a result inconsistent with the clinical picture",
                   "an error code presented during start-up",
                   "an unexpected shutdown during operation",
                   "a consumable failing to seat correctly"]},
    [("21 CFR 803.50", "manufacturer reporting of device-related deaths and serious injuries"),
     ("21 CFR 820.30", "design controls"),
     ("21 CFR 820.198", "complaint files"),
     ("21 CFR 820.100", "corrective and preventive action"),
     ("21 CFR 807.92", "content of a 510(k) summary"),
     ("ISO 13485 Clause 8.2.2", "complaint handling within the quality management system"),
     ("ISO 14971 Clause 7", "evaluation of overall residual risk acceptability")],
    ["the complaint handling system", "the quality management system",
     "the design control repository", "the post-market surveillance database",
     "the document control system", "the field action tracker"],
    ["Director of Regulatory Affairs", "Quality Systems Manager",
     "Design Assurance Engineer", "Complaint Handling Specialist",
     "Post-Market Surveillance Lead", "Risk Management Lead",
     "Clinical Affairs Manager", "Manufacturing Quality Engineer"],
    ["What is the intended use of the QM-100 Analyser?",
     "Which clearance covers this device?",
     "What substances interfere with the measurement?",
     "Was this complaint determined reportable?",
     "What hazard does this risk control address?",
     "Which CAPA arose from the complaint trend?",
     "What are the complaint file requirements?",
     "Which predicate device was cited?",
     "What limitation is stated in the instructions for use?",
     "How is residual risk judged acceptable?"],
)


# ================================================================== BANKING
_BK_OBLIG = [f"OBL-{100 + i * 13:03d}" for i in range(10)]
_BK_TOPIC = ["Customer Due Diligence", "Transaction Monitoring", "Credit Risk Rating",
             "Collateral Valuation", "Complaints Handling", "Model Risk Governance",
             "Outsourcing Oversight", "Operational Resilience", "Conduct and Suitability",
             "Records Retention"]
_BK_CTRL = [f"CTL-{400 + i * 17:03d}" for i in range(10)]

BANKING = _pack(
    "banking",
    {"obligation": _BK_OBLIG, "topic": _BK_TOPIC, "control": _BK_CTRL},
    [
        {"name": "Regulatory Obligation Record", "count_share": 1.3,
         "id": lambda c: c["obligation"],
         "title": lambda c: f"Obligation — {c['topic']} ({c['obligation']})",
         "sections": [("Obligation and Interpretation", lambda c:
            f"{c['tenant']} is required to maintain arrangements covering {c['topic']}.\n\n"
            f"Source: {c['reg'][0]} — {c['reg'][1]}.\n\n"
            f"Interpretation: the obligation requires that {c['requirement']}. It is "
            f"discharged operationally through control {c['control']}.\n\n"
            f"Breach of this obligation is reportable to the {c['approver']} "
            f"{c['timeframe']}.")]},

        {"name": "Internal Control Description", "count_share": 1.2,
         "id": lambda c: c["control"],
         "title": lambda c: f"Control — {c['topic']} ({c['control']})",
         "sections": [("Control Objective and Operation", lambda c:
            f"Control {c['control']} exists to satisfy obligation {c['obligation']} "
            f"concerning {c['topic']}.\n\n"
            f"Implements policy {c['ref']('Credit Policy Section')} and is executed through "
            f"{c['ref']('Procedure Document')}.\n\n"
            f"Objective: ensure that {c['requirement']}.\n\n"
            f"Operation: the control executes in {c['system']}. Exceptions are routed to "
            f"the {c['role']} for disposition {c['timeframe']}.\n\n"
            f"Testing: the control is tested on a sample basis; the reported measure is "
            f"{c['measure']}.")]},

        {"name": "Credit Policy Section", "count_share": 1.1,
         "id": lambda c: f"CPOL-{c['idx'] % 40 + 10:03d}",
         "title": lambda c: f"Credit Policy — {c['topic']}",
         "sections": [("Policy Requirement", lambda c:
            f"It is the policy of {c['tenant']} that {c['requirement']} before an "
            f"exposure is approved.\n\n"
            f"Exceptions require approval at the delegated authority level and must be "
            f"recorded with rationale in {c['system']}.\n\n"
            f"This policy discharges obligation {c['obligation']} and is evidenced "
            f"through control {c['control']}.")]},

        {"name": "Procedure Document", "count_share": 1.1,
         "id": lambda c: f"PROC-{c['idx'] % 50 + 200:03d}",
         "title": lambda c: f"Procedure — {c['topic']} Execution",
         "sections": [("Procedure", lambda c:
            f"1. Confirm the customer or exposure is in scope for {c['topic']}.\n"
            f"2. Perform the assessment in {c['system']} using the approved template.\n"
            f"3. Verify that {c['requirement']}.\n"
            f"4. Where the standard is not met, escalate {c['timeframe']}.\n"
            f"5. Record the outcome so that control {c['control']} can be evidenced.")]},

        {"name": "Model Documentation", "count_share": 0.9,
         "id": lambda c: f"MOD-{c['idx'] % 30 + 1:03d}",
         "title": lambda c: f"Model Documentation — {c['topic']} Model",
         "sections": [("Purpose, Limitations and Validation", lambda c:
            f"This model supports decisions concerning {c['topic']} and operates within "
            f"{c['system']}.\n\n"
            f"Known limitation: performance degrades where the input population differs "
            f"materially from the development sample. Compensating control: {c['control']}.\n\n"
            f"Independent validation confirmed the model is fit for purpose. Governance "
            f"follows {c['reg'][0]} — {c['reg'][1]}. Ongoing monitoring reports "
            f"{c['measure']}.")]},

        {"name": "Control Testing Result", "count_share": 1.0,
         "id": lambda c: f"CTR-{2024 + c['idx'] % 3}-{c['idx'] % 60 + 1:03d}",
         "title": lambda c: f"Control Testing — {c['topic']} ({c['control']})",
         "sections": [("Test Approach and Result", lambda c:
            f"Testing of control {c['control']}, which discharges obligation "
            f"{c['obligation']}.\n\n"
            f"Approach: a sample of executions was re-performed to confirm that "
            f"{c['requirement']}.\n\n"
            f"Result: the control operated as designed in the majority of the sample. "
            f"Exceptions related to escalations not raised {c['timeframe']}.\n\n"
            f"Reported measure: {c['measure']}. Owner: {c['role']}.")]},

        {"name": "Audit Issue", "count_share": 0.9,
         "id": lambda c: f"AI-{2024 + c['idx'] % 3}-{c['idx'] % 50 + 1:03d}",
         "title": lambda c: f"Audit Issue — {c['topic']}",
         "sections": [("Issue and Management Response", lambda c:
            f"Internal audit reviewed arrangements for {c['topic']}.\n\n"
            f"Issue: control {c['control']} did not consistently evidence that {c['requirement']}, "
            f"weakening reliance for obligation {c['obligation']}. Control description: "
            f"{c['ref']('Internal Control Description')}.\n\n"
            f"Regulatory relevance: {c['reg'][0]} — {c['reg'][1]}.\n\n"
            f"Management response: strengthen the evidencing step in {c['system']} and "
            f"re-test. Accountable executive: {c['approver']}.")]},

        {"name": "Committee Paper", "count_share": 0.8,
         "id": lambda c: f"CP-{2024 + c['idx'] % 3}-{c['idx'] % 12 + 1:02d}",
         "title": lambda c: f"Committee Paper — {c['topic']} Oversight",
         "sections": [("Position and Recommendation", lambda c:
            f"This paper updates the committee on {c['topic']}.\n\n"
            f"Position: control {c['control']} is operating, with residual weakness in "
            f"evidencing. The reported measure is {c['measure']}.\n\n"
            f"Obligation {c['obligation']} remains discharged, though reliance is "
            f"qualified pending remediation.\n\n"
            f"Recommendation: approve the remediation plan and receive a further update "
            f"{c['timeframe']}.")]},
    ],
    {"requirement": ["identity is verified and the source of funds is understood before onboarding",
                     "exposures are rated using the approved methodology and reviewed at least annually",
                     "alerts are dispositioned by a competent reviewer with documented rationale",
                     "collateral is valued using an independent source at the required frequency",
                     "complaints are acknowledged and resolved within the published service standard",
                     "material outsourcing arrangements are subject to due diligence and ongoing monitoring"],
     "measure": ["the proportion of executions with complete evidence retained",
                 "the median days from alert to disposition",
                 "the exception rate against the approved standard",
                 "the proportion of reviews completed within the required period"],
     "timeframe": ["within five business days", "by the end of the following month",
                   "within 24 hours of identification", "at the next scheduled committee"]},
    [("SR 11-7", "supervisory guidance on model risk management"),
     ("12 CFR 21.21", "programme for monitoring compliance with the Bank Secrecy Act"),
     ("12 CFR 30 Appendix D", "standards for risk governance"),
     ("Sarbanes-Oxley Section 404", "management assessment of internal controls"),
     ("Basel Committee BCBS 239", "principles for effective risk data aggregation"),
     ("12 CFR 1026", "truth in lending disclosure requirements")],
    ["the core banking platform", "the transaction monitoring system",
     "the credit origination workflow", "the governance risk and compliance platform",
     "the customer onboarding portal", "the model inventory"],
    ["Head of Regulatory Compliance", "Chief Risk Officer", "Head of Internal Audit",
     "Credit Policy Director", "Financial Crime Lead", "Model Risk Manager",
     "Operational Risk Manager", "Control Owner", "Business Line COO"],
    ["Which control satisfies the customer due diligence obligation?",
     "What is the escalation timeframe for a control exception?",
     "Which regulation requires model validation?",
     "What did internal audit find on transaction monitoring?",
     "Who approves a credit policy exception?",
     "How is control effectiveness measured?",
     "What limitation is documented for the credit rating model?",
     "Which obligation does this control discharge?",
     "What is the complaints resolution standard?",
     "What remediation was agreed for the audit issue?"],
)


# ================================================================ INSURANCE
_IN_FORMS = [f"QF-{200 + i * 11:03d}" for i in range(10)]
_IN_LINES = ["Commercial Property", "General Liability", "Cyber Liability",
             "Professional Indemnity", "Marine Cargo", "Motor Fleet",
             "Business Interruption", "Directors and Officers",
             "Employers Liability", "Engineering All Risks"]

INSURANCE = _pack(
    "insurance",
    {"form": _IN_FORMS, "line": _IN_LINES},
    [
        {"name": "Policy Wording", "count_share": 1.4,
         "id": lambda c: c["form"],
         "title": lambda c: f"Policy Wording — {c['line']} ({c['form']})",
         "sections": [("Insuring Agreement", lambda c:
            f"{c['tenant']} agrees to indemnify the insured in respect of {c['line']} "
            f"loss occurring during the period of insurance, subject to the terms, "
            f"conditions and exclusions of form {c['form']}.\n\n"
            f"Cover operates on the basis stated in the schedule, subject to the limit "
            f"and the deductible shown."),
          ("Exclusions and Conditions", lambda c:
            f"This policy does not cover loss {c['exclusion']}.\n\n"
            f"It is a condition precedent to liability that the insured "
            f"{c['condition']}. Failure to comply may entitle the insurer to decline or "
            f"reduce a claim.\n\n"
            f"Notification: the insured must notify the insurer of any circumstance "
            f"likely to give rise to a claim {c['timeframe']}.")]},

        {"name": "Endorsement", "count_share": 1.1,
         "id": lambda c: f"END-{c['form'].split('-')[1]}-{c['idx'] % 40 + 1:02d}",
         "title": lambda c: f"Endorsement — {c['line']} ({c['form']})",
         "sections": [("Amendment", lambda c:
            f"Form {c['form']} is amended as follows with effect from the date shown.\n\n"
            f"The exclusion concerning loss {c['exclusion']} in form {c['form']} is amended to "
            f"apply only where the insured has failed to {c['condition']}. Handling "
            f"guidance: {c['ref']('Claims Handling Instruction')}.\n\n"
            f"All other terms, conditions and exclusions of the policy remain unaltered.")]},

        {"name": "Underwriting Guideline", "count_share": 1.2,
         "id": lambda c: f"UWG-{c['idx'] % 40 + 100:03d}",
         "title": lambda c: f"Underwriting Guideline — {c['line']}",
         "sections": [("Appetite and Referral", lambda c:
            f"Appetite for {c['line']} written on form {c['form']} is described below.\n\n"
            f"In appetite where the risk presents no aggravating feature and the insured "
            f"can evidence that they {c['condition']}.\n\n"
            f"Refer to the {c['approver']} where the exposure exceeds the delegated "
            f"limit, or where the risk involves circumstances that would engage the "
            f"exclusion concerning loss {c['exclusion']}.\n\n"
            f"Pricing is derived in {c['system']} using the approved rating basis.")]},

        {"name": "Claims Handling Instruction", "count_share": 1.2,
         "id": lambda c: f"CHI-{c['idx'] % 40 + 300:03d}",
         "title": lambda c: f"Claims Handling — {c['line']} ({c['form']})",
         "sections": [("Handling Standard", lambda c:
            f"On notification of a claim under form {c['form']}, the handler must:\n\n"
            f"1. Confirm cover was in force and the loss falls within the insuring "
            f"agreement.\n"
            f"2. Check whether the exclusion concerning loss {c['exclusion']} is engaged.\n"
            f"3. Verify that the insured complied with the condition precedent to "
            f"{c['condition']}.\n"
            f"4. Reserve in {c['system']} within the required interval.\n"
            f"5. Acknowledge to the insured {c['timeframe']}.\n\n"
            f"Coverage declinature requires sign-off by the {c['approver']}.")]},

        {"name": "Coverage Position", "count_share": 1.0,
         "id": lambda c: f"CVP-{2024 + c['idx'] % 3}-{c['idx'] % 50 + 1:03d}",
         "title": lambda c: f"Coverage Position — {c['line']} Claim",
         "sections": [("Analysis and Position", lambda c:
            f"Claim notified under form {c['form']} ({c['line']}).\n\n"
            f"Assessed under form {c['form']} following {c['ref']('Claims Handling Instruction')}.\n\n"
            f"Analysis: the loss falls within the insuring agreement. However the "
            f"exclusion concerning loss {c['exclusion']} is engaged on the facts as "
            f"presently understood.\n\n"
            f"Further, it is not evident that the insured complied with the condition "
            f"precedent to {c['condition']}.\n\n"
            f"Position: reserve the insurer's rights pending further information; do not "
            f"decline without sign-off by the {c['approver']}.")]},

        {"name": "Reinsurance Treaty Summary", "count_share": 0.8,
         "id": lambda c: f"RI-{2024 + c['idx'] % 3}-{c['idx'] % 20 + 1:02d}",
         "title": lambda c: f"Reinsurance Summary — {c['line']} Programme",
         "sections": [("Structure and Application", lambda c:
            f"The {c['line']} account written on form {c['form']} is protected by an "
            f"excess of loss programme.\n\n"
            f"The programme attaches above the retention and responds per event, subject "
            f"to the reinstatement provisions.\n\n"
            f"Claims exceeding the attachment must be notified to reinsurers "
            f"{c['timeframe']}. Notification is recorded in {c['system']}.")]},

        {"name": "Product Governance Record", "count_share": 0.9,
         "id": lambda c: f"PG-{c['form'].split('-')[1]}-{c['idx'] % 30 + 1:02d}",
         "title": lambda c: f"Product Governance — {c['line']} ({c['form']})",
         "sections": [("Target Market and Review", lambda c:
            f"Form {c['form']} is designed for the {c['line']} target market described "
            f"in the product approval.\n\n"
            f"The exclusion concerning loss {c['exclusion']} was assessed as consistent "
            f"with the needs of the target market and is disclosed prominently.\n\n"
            f"Review confirmed the product continues to deliver fair value. Governance "
            f"follows {c['reg'][0]} — {c['reg'][1]}. Next review is scheduled "
            f"{c['timeframe']}.")]},

        {"name": "Actuarial Reserving Note", "count_share": 0.8,
         "id": lambda c: f"ARN-{2024 + c['idx'] % 3}-{c['idx'] % 20 + 1:02d}",
         "title": lambda c: f"Reserving Note — {c['line']}",
         "sections": [("Assumptions and Uncertainty", lambda c:
            f"Reserving note for the {c['line']} account written on form {c['form']}.\n\n"
            f"The principal uncertainty concerns the frequency with which the exclusion "
            f"regarding loss {c['exclusion']} is successfully applied at claim stage.\n\n"
            f"Where coverage positions are resolved against the insurer, ultimate cost "
            f"increases materially. Sensitivity has been tested and is disclosed.\n\n"
            f"Prepared by the {c['role']} and reviewed by the {c['approver']}.")]},
    ],
    {"exclusion": ["arising from wear, tear or gradual deterioration",
                   "arising from a deliberate act of the insured or their representative",
                   "consequent upon the failure of a system the insured knew to be defective",
                   "arising from circumstances notified under a previous policy",
                   "arising from contractual liability assumed beyond that imposed by law",
                   "arising from an unrepaired defect identified at a prior survey"],
     "condition": ["maintain the protections described in the proposal",
                   "notify any material change in the risk during the period",
                   "keep records sufficient to substantiate a claim",
                   "comply with all statutory requirements applicable to the operation"],
     "timeframe": ["as soon as reasonably practicable and in any event within 30 days",
                   "within five business days of notification",
                   "before the expiry of the period of insurance",
                   "within 14 days"]},
    [("Solvency II Article 45", "own risk and solvency assessment"),
     ("Solvency II Article 41", "general governance requirements"),
     ("IFRS 17", "measurement and presentation of insurance contracts"),
     ("Insurance Distribution Directive Article 25", "product oversight and governance"),
     ("Insurance Distribution Directive Article 20", "demands and needs assessment")],
    ["the policy administration system", "the claims management system",
     "the underwriting workbench", "the rating engine",
     "the reinsurance administration system", "the document library"],
    ["Chief Underwriting Officer", "Claims Operations Director", "Head of Product Governance",
     "Chief Actuary", "Reinsurance Manager", "Coverage Counsel",
     "Portfolio Underwriter", "Claims Technical Lead"],
    ["Which exclusion applies to this claim?",
     "What is the condition precedent to liability?",
     "When must the insured notify a circumstance?",
     "What is the underwriting appetite for cyber liability?",
     "Which endorsement amended the wear and tear exclusion?",
     "Who signs off a coverage declinature?",
     "How does the reinsurance programme respond?",
     "What is the target market for this product?",
     "What reserving uncertainty relates to this exclusion?",
     "Which form governs the marine cargo account?"],
)


# ================================================================= MARITIME
_MR_VESSELS = ["MV Q-Aurora", "MV Q-Meridian", "MV Q-Solstice", "MV Q-Horizon",
               "MV Q-Zenith", "MV Q-Odyssey", "MV Q-Marina", "MV Q-Celeste",
               "MV Q-Pacifica", "MV Q-Aurelia"]
_MR_EQUIP = ["Main Engine No.1", "Auxiliary Generator No.2", "Bow Thruster",
             "Fire Detection System", "Lifeboat Davit No.3", "Sewage Treatment Plant",
             "Fresh Water Generator", "Ballast Water Treatment System",
             "Emergency Fire Pump", "Galley Ventilation Hood"]

MARITIME = _pack(
    "maritime",
    {"vessel": _MR_VESSELS, "equipment": _MR_EQUIP},
    [
        {"name": "Safety Management System Procedure", "count_share": 1.4,
         "id": lambda c: f"SMS-{c['idx'] % 50 + 100:03d}",
         "title": lambda c: f"SMS Procedure — {c['equipment']} Operation",
         "sections": [("Purpose and Responsibility", lambda c:
            f"This procedure forms part of the safety management system of {c['tenant']} "
            f"and applies to all vessels in the fleet, including {c['vessel']}.\n\n"
            f"The Master retains overriding authority. Day-to-day responsibility for the "
            f"{c['equipment']} rests with the {c['role']}.\n\n"
            f"Compliance is required under {c['reg'][0]} — {c['reg'][1]}."),
          ("Procedure and Records", lambda c:
            f"1. Confirm the {c['equipment']} is in the condition required before "
            f"operation.\n"
            f"2. Where {c['condition']}, do not operate and raise a defect record.\n"
            f"3. Record the check in {c['system']}.\n"
            f"4. Report any {c['finding']} to the {c['approver']} {c['timeframe']}.\n\n"
            f"Records are retained on board and ashore and are subject to review during "
            f"internal audit and external inspection.")]},

        {"name": "Planned Maintenance Record", "count_share": 1.3,
         "id": lambda c: f"PMS-{c['vessel'].split('-')[1][:3].upper()}-{c['idx'] % 60 + 1000:04d}",
         "title": lambda c: f"Maintenance Record — {c['equipment']} — {c['vessel']}",
         "sections": [("Work Performed", lambda c:
            f"Planned maintenance carried out on the {c['equipment']} aboard "
            f"{c['vessel']}.\n\n"
            f"Condition on inspection: {c['finding']}.\n\n"
            f"Action taken: the affected component was made good in accordance with the "
            f"maker's instructions. Spares consumed were recorded in {c['system']}.\n\n"
            f"The equipment was returned to service and function-tested satisfactorily. "
            f"Next due interval is set from the completion date.")]},

        {"name": "Port State Control Finding", "count_share": 1.0,
         "id": lambda c: f"PSC-{2024 + c['idx'] % 3}-{c['idx'] % 50 + 1:03d}",
         "title": lambda c: f"Inspection Finding — {c['vessel']} — {c['equipment']}",
         "sections": [("Deficiency and Rectification", lambda c:
            f"Deficiency recorded during inspection of {c['vessel']}.\n\n"
            f"Observation: {c['finding']} affecting the {c['equipment']} aboard {c['vessel']}. The "
            f"condition indicates that procedure {c['ref']('Safety Management System Procedure')} "
            f"was not followed as written. Maintenance history: "
            f"{c['ref']('Planned Maintenance Record')}.\n\n"
            f"Convention reference: {c['reg'][0]} — {c['reg'][1]}.\n\n"
            f"Rectification: action to be completed {c['timeframe']} and evidence "
            f"submitted to the {c['approver']}.")]},

        {"name": "Non-Conformity Report", "count_share": 1.0,
         "id": lambda c: f"NCR-{2024 + c['idx'] % 3}-{c['idx'] % 60 + 1:03d}",
         "title": lambda c: f"Non-Conformity — {c['equipment']} — {c['vessel']}",
         "sections": [("Non-Conformity and Corrective Action", lambda c:
            f"Non-conformity raised during internal audit of {c['vessel']}.\n\n"
            f"Detail: {c['finding']} concerning the {c['equipment']} aboard {c['vessel']}, where "
            f"{c['condition']} had not been actioned as required by procedure "
            f"{c['ref']('Safety Management System Procedure')}.\n\n"
            f"Root cause: the recording step in {c['system']} was not completed at the "
            f"time of the check.\n\n"
            f"Corrective action: reinforce the procedure and verify at the next internal "
            f"audit. Owner: {c['role']}.")]},

        {"name": "Emergency Drill Record", "count_share": 0.9,
         "id": lambda c: f"DRL-{c['vessel'].split('-')[1][:3].upper()}-{c['idx'] % 40 + 1:03d}",
         "title": lambda c: f"Drill Record — {c['equipment']} Emergency Response",
         "sections": [("Drill Conduct and Learning", lambda c:
            f"Drill conducted aboard {c['vessel']} exercising the emergency response "
            f"associated with the {c['equipment']}.\n\n"
            f"Participation met the required complement. Timings were within the "
            f"expected range.\n\n"
            f"Learning point: {c['finding']} was observed during the exercise. The "
            f"{c['role']} will address this at the next familiarisation session and "
            f"record completion in {c['system']}.")]},

        {"name": "Technical Manual Extract", "count_share": 0.9,
         "id": lambda c: f"TM-{c['idx'] % 40 + 500:03d}",
         "title": lambda c: f"Technical Manual — {c['equipment']}",
         "sections": [("Operating Limits and Maintenance", lambda c:
            f"Operating and maintenance information for the {c['equipment']} as fitted "
            f"to {c['vessel']} and sister vessels.\n\n"
            f"Do not operate where {c['condition']}. Operation outside the stated limits "
            f"may result in damage and invalidate the maker's warranty.\n\n"
            f"Planned maintenance intervals are stated in the maker's schedule and are "
            f"reflected in {c['system']}.")]},

        {"name": "Public Health Inspection Report", "count_share": 0.8,
         "id": lambda c: f"PHI-{2024 + c['idx'] % 3}-{c['idx'] % 30 + 1:03d}",
         "title": lambda c: f"Public Health Inspection — {c['vessel']}",
         "sections": [("Inspection Result", lambda c:
            f"Unannounced inspection of {c['vessel']} covering potable water, food "
            f"service, and associated systems including the {c['equipment']}.\n\n"
            f"Observation: {c['finding']}. The condition was corrected during the "
            f"inspection and verified before departure.\n\n"
            f"The vessel achieved a passing score. Follow-up items are tracked in "
            f"{c['system']} and reviewed by the {c['approver']} {c['timeframe']}.")]},

        {"name": "Guest Operations Procedure", "count_share": 0.8,
         "id": lambda c: f"GOP-{c['idx'] % 40 + 200:03d}",
         "title": lambda c: f"Guest Operations — Embarkation and Safety Briefing",
         "sections": [("Procedure", lambda c:
            f"This procedure governs guest embarkation aboard {c['vessel']} and the "
            f"associated safety briefing.\n\n"
            f"All guests must complete the briefing before departure. Attendance is "
            f"recorded in {c['system']} and reconciled against the manifest.\n\n"
            f"Where {c['condition']}, embarkation is paused and the {c['role']} is "
            f"notified {c['timeframe']}.\n\n"
            f"Requirement basis: {c['reg'][0]} — {c['reg'][1]}.")]},
    ],
    {"finding": ["a maintenance record completed without the verifying signature",
                 "a corroded securing arrangement noted on visual inspection",
                 "an expired calibration label on a monitoring instrument",
                 "an obstruction to an escape route noted during rounds",
                 "a temperature log with a gap over the preceding period",
                 "a spare part fitted without the traceability record"],
     "condition": ["the equipment shows evidence of damage or leakage",
                   "the required certificate is not valid",
                   "the crew member has not completed the associated familiarisation",
                   "the monitoring instrument is outside its calibration interval"],
     "timeframe": ["before the next port of call", "within 14 days",
                   "before the vessel next sails", "at the next scheduled review"]},
    [("ISM Code Section 7", "development of plans for shipboard operations"),
     ("ISM Code Section 9", "reports and analysis of non-conformities and accidents"),
     ("ISM Code Section 10", "maintenance of the ship and equipment"),
     ("SOLAS Chapter III Regulation 19", "emergency training and drills"),
     ("SOLAS Chapter II-2", "fire protection, detection and extinction"),
     ("MARPOL Annex IV", "prevention of pollution by sewage from ships"),
     ("MLC 2006 Regulation 3.1", "accommodation and recreational facilities")],
    ["the planned maintenance system", "the fleet management system",
     "the electronic logbook", "the safety reporting database",
     "the crew training record system", "the guest services platform"],
    ["Director of Marine Operations", "Designated Person Ashore", "Master",
     "Chief Engineer", "Safety Officer", "Fleet Technical Superintendent",
     "Hotel Operations Manager", "HSQE Manager", "Staff Captain"],
    ["Which procedure covers the fire detection system?",
     "What deficiency was recorded at the last inspection?",
     "When must a non-conformity be rectified?",
     "Who has overriding authority aboard the vessel?",
     "What maintenance was carried out on the auxiliary generator?",
     "Which convention requires emergency drills?",
     "What root cause was identified for the audit non-conformity?",
     "What are the operating limits for the ballast water treatment system?",
     "How is drill attendance recorded?",
     "What follow-up is required after the public health inspection?"],
)


# ==================================================================== RETAIL
_RT_ARTICLES = [f"ART-{80000 + i * 731:05d}" for i in range(10)]
_RT_CATS = ["Chilled Ready Meals", "Household Cleaning", "Children's Nightwear",
            "Small Kitchen Appliances", "Fresh Produce", "Personal Care",
            "Toys and Games", "Outdoor Furniture", "Bakery", "Pet Food"]
_RT_VENDORS = [f"VEN-{2000 + i * 137:04d}" for i in range(10)]

RETAIL = _pack(
    "retail",
    {"article": _RT_ARTICLES, "category": _RT_CATS, "vendor": _RT_VENDORS},
    [
        {"name": "Vendor Compliance Requirement", "count_share": 1.3,
         "id": lambda c: f"VCR-{c['idx'] % 40 + 100:03d}",
         "title": lambda c: f"Vendor Requirement — {c['category']}",
         "sections": [("Requirement", lambda c:
            f"Vendors supplying {c['category']} to {c['tenant']}, including vendor "
            f"{c['vendor']}, must comply with the requirements in this document.\n\n"
            f"Every article must {c['requirement']}. Evidence must be available for "
            f"inspection {c['timeframe']}.\n\n"
            f"Non-compliance may result in the affected article being blocked at goods "
            f"receipt and a chargeback applied."),
          ("Traceability", lambda c:
            f"Each despatch must carry the article identifier and the location "
            f"identifier so that a unit can be traced from source to shelf.\n\n"
            f"Data is exchanged through {c['system']}. Where {c['issue']}, the despatch "
            f"is held pending correction.")]},

        {"name": "Product Specification", "count_share": 1.3,
         "id": lambda c: c["article"],
         "title": lambda c: f"Product Specification — {c['category']} ({c['article']})",
         "sections": [("Specification", lambda c:
            f"Specification for article {c['article']} in the {c['category']} range, "
            f"supplied by vendor {c['vendor']}.\n\n"
            f"The article must {c['requirement']}. Storage and handling requirements are "
            f"stated on the pack and must be observed throughout the chain.\n\n"
            f"Any change to the specification requires re-approval before the amended "
            f"article is despatched."),
          ("Verification", lambda c:
            f"Conformance is verified at approval and on a sampling basis thereafter. "
            f"Results are recorded in {c['system']}.\n\n"
            f"Where {c['issue']} is identified, the article is placed on hold and the "
            f"{c['approver']} is notified {c['timeframe']}.")]},

        {"name": "Store Operating Instruction", "count_share": 1.2,
         "id": lambda c: f"SOI-{c['idx'] % 50 + 300:03d}",
         "title": lambda c: f"Store Instruction — {c['category']} Handling",
         "sections": [("Instruction", lambda c:
            f"1. On delivery, check that the article identifier matches the despatch "
            f"record.\n"
            f"2. Confirm the article meets the requirement that it {c['requirement']}.\n"
            f"3. Where {c['issue']}, quarantine the stock and record it in {c['system']}.\n"
            f"4. Escalate to the {c['role']} {c['timeframe']}.\n"
            f"5. Do not return quarantined stock to sale without authorisation.")]},

        {"name": "Product Recall Notice", "count_share": 0.9,
         "id": lambda c: f"RCL-{2024 + c['idx'] % 3}-{c['idx'] % 30 + 1:03d}",
         "title": lambda c: f"Recall Notice — {c['category']} ({c['article']})",
         "sections": [("Recall Detail and Action", lambda c:
            f"{c['tenant']} is recalling article {c['article']} in the {c['category']} "
            f"range, supplied by vendor {c['vendor']}.\n\n"
            f"Reason: {c['issue']}, meaning article {c['article']} does not {c['requirement']}. "
            f"Specification: {c['ref']('Product Specification')}; vendor requirement: "
            f"{c['ref']('Vendor Compliance Requirement')}.\n\n"
            f"Stores must remove affected stock from sale immediately, record the "
            f"quantity in {c['system']}, and display the customer notice at the point of "
            f"sale.\n\n"
            f"Regulatory notification made under {c['reg'][0]} — {c['reg'][1]}.")]},

        {"name": "Supplier Audit Report", "count_share": 1.0,
         "id": lambda c: f"SAR-{2024 + c['idx'] % 3}-{c['vendor'].split('-')[1]}",
         "title": lambda c: f"Supplier Audit — Vendor {c['vendor']} ({c['category']})",
         "sections": [("Findings", lambda c:
            f"Audit of vendor {c['vendor']} supplying {c['category']} including article "
            f"{c['article']}.\n\n"
            f"Finding: {c['issue']}. Vendor {c['vendor']} could not demonstrate that article "
            f"{c['article']} will {c['requirement']}. Requirement reference: "
            f"{c['ref']('Vendor Compliance Requirement')}.\n\n"
            f"Severity: major. Corrective action required {c['timeframe']}, with evidence "
            f"submitted through {c['system']}.\n\n"
            f"Follow-up audit scheduled. Accountable: {c['approver']}.")]},

        {"name": "Merchandising Guide", "count_share": 0.9,
         "id": lambda c: f"MG-{c['idx'] % 40 + 400:03d}",
         "title": lambda c: f"Merchandising Guide — {c['category']}",
         "sections": [("Layout and Compliance", lambda c:
            f"Merchandising standard for the {c['category']} range, including article "
            f"{c['article']}.\n\n"
            f"Adjacency rules must be observed so that the article continues to "
            f"{c['requirement']} in the store environment.\n\n"
            f"Where {c['issue']} arises on the shop floor, follow the store operating "
            f"instruction rather than the layout guide.")]},

        {"name": "Traceability Record", "count_share": 0.9,
         "id": lambda c: f"TRC-{c['article'].split('-')[1]}-{c['idx'] % 40 + 1:03d}",
         "title": lambda c: f"Traceability — {c['article']} ({c['category']})",
         "sections": [("Chain of Custody", lambda c:
            f"Traceability record for article {c['article']} from vendor {c['vendor']} "
            f"to store.\n\n"
            f"Events captured include despatch, receipt at the distribution centre, and "
            f"receipt at store. Each event carries the article and location identifiers.\n\n"
            f"This record supports withdrawal at lot level. Where {c['issue']}, the "
            f"affected lots can be identified without withdrawing the whole range.\n\n"
            f"Data is held in {c['system']} in accordance with {c['reg'][0]}.")]},

        {"name": "Safety Data Sheet Summary", "count_share": 0.7,
         "id": lambda c: f"SDS-{c['article'].split('-')[1]}",
         "title": lambda c: f"Safety Data Summary — {c['category']} ({c['article']})",
         "sections": [("Handling and Storage", lambda c:
            f"Summary safety information for article {c['article']}.\n\n"
            f"Store in accordance with the stated conditions. The article must "
            f"{c['requirement']} throughout storage and display.\n\n"
            f"In the event of spillage or damage, follow the store operating instruction "
            f"and record in {c['system']}. Notify the {c['role']} {c['timeframe']}.")]},
    ],
    {"requirement": ["carry the correct allergen declaration on the outer pack",
                     "meet the applicable flammability performance standard",
                     "be labelled with the country of origin and the batch identifier",
                     "be maintained within the stated temperature range at all times",
                     "carry the age grading and associated safety warnings",
                     "be free from the restricted substances listed in the schedule"],
     "issue": ["a labelling discrepancy identified at goods receipt",
               "a temperature excursion recorded during transit",
               "a batch identifier that could not be reconciled to the despatch record",
               "a test certificate that had expired at the point of despatch",
               "an unapproved change to the component specification"],
     "timeframe": ["within 48 hours", "before the next despatch",
                   "within five working days", "at the next scheduled review"]},
    [("General Product Safety requirements", "obligation to place only safe products on the market"),
     ("Food traceability requirements", "one-step-back and one-step-forward traceability records"),
     ("Textile labelling requirements", "fibre composition and care labelling"),
     ("Toy safety requirements", "age grading, warnings and conformity assessment"),
     ("Restricted substances schedule", "limits on substances of concern in consumer articles")],
    ["the vendor portal", "the product information management system",
     "the store stock system", "the quality management platform",
     "the traceability event repository", "the recall coordination tool"],
    ["VP Supply Chain Compliance", "Technical Manager", "Category Buyer",
     "Store Operations Manager", "Product Safety Lead", "Supplier Quality Auditor",
     "Regulatory Affairs Specialist", "Distribution Centre Manager"],
    ["What are the vendor requirements for children's nightwear?",
     "Which article is affected by this recall?",
     "What must a store do when stock is quarantined?",
     "Which vendor supplied this article?",
     "What labelling is required for this category?",
     "What finding was raised at the last supplier audit?",
     "How is lot-level traceability maintained?",
     "What temperature range applies to chilled ready meals?",
     "Who must be notified when a specification change occurs?",
     "What is the corrective action timeframe for a major finding?"],
)


# ================================================================== QUALITY
_QA_REQS = [f"REQ-{1000 + i * 37:04d}" for i in range(10)]
_QA_FEATURES = ["Guest Booking Flow", "Payment Authorisation", "Loyalty Accrual",
                "Identity Verification", "Search and Filter", "Notification Delivery",
                "Offline Synchronisation", "Accessibility Compliance",
                "Session Management", "Reporting Export"]
_QA_SUITES = [f"TS-{300 + i * 11:03d}" for i in range(10)]

QUALITY = _pack(
    "quality",
    {"req": _QA_REQS, "feature": _QA_FEATURES, "suite": _QA_SUITES},
    [
        {"name": "Test Strategy", "count_share": 1.1,
         "id": lambda c: f"STRAT-{c['idx'] % 20 + 1:02d}",
         "title": lambda c: f"Test Strategy — {c['feature']}",
         "sections": [("Approach and Scope", lambda c:
            f"This strategy describes how {c['tenant']} assures the {c['feature']} "
            f"capability against requirement {c['req']}.\n\n"
            f"The approach applies {c['technique']} at the level where defects are "
            f"cheapest to detect, supported by exploratory testing around the areas of "
            f"highest change.\n\n"
            f"Alignment: {c['reg'][0]} — {c['reg'][1]}."),
          ("Entry, Exit and Risk", lambda c:
            f"Entry criteria: the build is deployed and smoke tests pass.\n\n"
            f"Exit criteria: {c['exit']}. Residual risk is documented and accepted by the "
            f"{c['approver']}.\n\n"
            f"Principal risk: {c['risk']}. Mitigation is addressed through suite "
            f"{c['suite']}.")]},

        {"name": "Test Plan", "count_share": 1.2,
         "id": lambda c: f"PLAN-{c['suite'].split('-')[1]}",
         "title": lambda c: f"Test Plan — {c['feature']} ({c['suite']})",
         "sections": [("Scope and Schedule", lambda c:
            f"Test plan for suite {c['suite']} covering the {c['feature']} capability "
            f"and requirement {c['req']}.\n\n"
            f"In scope: functional verification, regression around adjacent capability, "
            f"and {c['technique']}.\n\n"
            f"Out of scope: performance characterisation, addressed separately.\n\n"
            f"Execution is tracked in {c['system']}; defects are raised in the same tool "
            f"and linked to the covering test case.")]},

        {"name": "Test Case Specification", "count_share": 1.5,
         "id": lambda c: f"TC-{c['req'].split('-')[1]}-{c['idx'] % 60 + 1:03d}",
         "title": lambda c: f"Test Case — {c['feature']} ({c['req']})",
         "sections": [("Preconditions and Steps", lambda c:
            f"Covers requirement {c['req']} within suite {c['suite']}.\n\n"
            f"Executed under plan {c['ref']('Test Plan')} within suite {c['suite']}.\n\n"
            f"Precondition: the account is provisioned and the {c['feature'].lower()} "
            f"capability is enabled.\n\n"
            f"1. Navigate to the capability under test.\n"
            f"2. Apply the input condition derived using {c['technique']}.\n"
            f"3. Submit and observe the system response.\n"
            f"4. Verify the outcome against the acceptance criterion.\n\n"
            f"Expected result: the system behaves as specified and no error is presented "
            f"to the user.")]},

        {"name": "Defect Report", "count_share": 1.3,
         "id": lambda c: f"DEF-{2024 + c['idx'] % 3}-{6000 + c['idx']:05d}",
         "title": lambda c: f"Defect — {c['feature']} ({c['req']})",
         "sections": [("Observation and Analysis", lambda c:
            f"Raised during execution of suite {c['suite']} against requirement "
            f"{c['req']}.\n\n"
            f"Detected by suite {c['suite']} executing {c['ref']('Test Case Specification')} "
            f"against requirement {c['req']}.\n\n"
            f"Observation: {c['symptom']}.\n\n"
            f"Analysis: the condition arises where {c['risk']}. The covering test case "
            f"detected the condition, but earlier stages did not.\n\n"
            f"Recommendation: strengthen coverage at the lower level using "
            f"{c['technique']} so the condition is caught before system test.")]},

        {"name": "Requirements Traceability Matrix", "count_share": 0.9,
         "id": lambda c: f"RTM-{c['idx'] % 20 + 1:02d}",
         "title": lambda c: f"Traceability Matrix — {c['feature']}",
         "sections": [("Coverage", lambda c:
            f"Traceability for the {c['feature']} capability.\n\n"
            f"Requirement {c['req']} is covered by suite {c['suite']}, which contains "
            f"functional and negative cases derived using {c['technique']}.\n\n"
            f"Where a requirement has no covering case, the gap is recorded and "
            f"prioritised against {c['risk']}.\n\n"
            f"The matrix is regenerated from {c['system']} at each release checkpoint.")]},

        {"name": "Automation Framework Guide", "count_share": 0.9,
         "id": lambda c: f"AFG-{c['idx'] % 20 + 1:02d}",
         "title": lambda c: f"Automation Guide — {c['feature']} Suite",
         "sections": [("Structure and Conventions", lambda c:
            f"Automation supporting suite {c['suite']} for the {c['feature']} "
            f"capability.\n\n"
            f"Tests are written against stable selectors and are independent of execution "
            f"order. Data is provisioned by the setup fixture and cleaned down "
            f"afterwards.\n\n"
            f"A test that fails intermittently is quarantined rather than retried, and "
            f"raised as a defect. Unaddressed flakiness erodes trust in the suite faster "
            f"than a missing test does.\n\n"
            f"Execution reports to {c['system']} at each pipeline run.")]},

        {"name": "Test Summary Report", "count_share": 1.0,
         "id": lambda c: f"TSR-{2024 + c['idx'] % 3}-{c['suite'].split('-')[1]}",
         "title": lambda c: f"Test Summary — {c['feature']} ({c['suite']})",
         "sections": [("Outcome and Recommendation", lambda c:
            f"Summary of execution for suite {c['suite']} covering requirement "
            f"{c['req']}.\n\n"
            f"Coverage of the planned scope was achieved. Defects raised were "
            f"predominantly associated with {c['risk']}.\n\n"
            f"Exit assessment: {c['exit']}.\n\n"
            f"Recommendation: proceed to release with the residual risk documented and "
            f"accepted by the {c['approver']}.")]},

        {"name": "Quality Process Standard", "count_share": 0.8,
         "id": lambda c: f"QPS-{c['idx'] % 20 + 100:03d}",
         "title": lambda c: f"Process Standard — Test Documentation",
         "sections": [("Standard", lambda c:
            f"This standard defines the documentation {c['tenant']} produces for a test "
            f"engagement, aligned to {c['reg'][0]} — {c['reg'][1]}.\n\n"
            f"Each engagement produces a strategy, a plan per suite, specifications for "
            f"each case, and a summary report. Every case traces to a requirement such "
            f"as {c['req']}.\n\n"
            f"Documentation is held in {c['system']} and is auditable for the retention "
            f"period.")]},
    ],
    {"technique": ["equivalence partitioning and boundary value analysis",
                   "decision table testing", "state transition testing",
                   "pairwise combination testing", "risk-based exploratory charters"],
     "risk": ["concurrent updates to the same record from two sessions",
              "a downstream service returning a partial response",
              "locale and time-zone handling at the day boundary",
              "an interrupted network during a multi-step submission",
              "cached state surviving a change of authenticated user"],
     "symptom": ["the confirmation is presented although the downstream write failed",
                 "the total displayed does not match the total recorded",
                 "the interface remains in a loading state indefinitely",
                 "an error message is presented that does not describe the actual fault",
                 "a previously entered value reappears after a session change"],
     "exit": ["all planned cases executed with no open severity-one defects",
              "coverage of the agreed scope achieved with residual risk documented",
              "regression suite green across two consecutive pipeline runs"]},
    [("ISO/IEC/IEEE 29119-2", "test processes across organisational, management and dynamic levels"),
     ("ISO/IEC/IEEE 29119-3", "test documentation templates and content"),
     ("ISO/IEC/IEEE 29119-4", "test design techniques"),
     ("ISO/IEC 25010", "product quality characteristics and sub-characteristics"),
     ("ISO/IEC/IEEE 29119-1", "concepts and definitions for software testing")],
    ["the test management tool", "the defect tracker", "the pipeline reporting dashboard",
     "the requirements repository", "the automation execution grid",
     "the release readiness board"],
    ["Head of Quality Engineering", "Test Manager", "Automation Lead",
     "Principal Test Consultant", "Release Manager", "Product Owner",
     "Performance Engineer", "Accessibility Specialist"],
    ["Which test cases cover this requirement?",
     "What is the exit criterion for this suite?",
     "What defect was found in the payment authorisation flow?",
     "Which technique was used to derive these cases?",
     "What is the principal risk on the booking flow?",
     "How is a flaky test handled?",
     "Which standard governs our test documentation?",
     "Where is the traceability gap for this feature?",
     "What was the recommendation in the test summary?",
     "Who accepts residual risk at release?"],
)


PACKS = {
    "pharma": PHARMA, "devices": DEVICES, "banking": BANKING,
    "insurance": INSURANCE, "maritime": MARITIME, "retail": RETAIL,
    "quality": QUALITY,
}
