<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Decision Support Rule — Heart Failure Admission and Transition

**Document number:** CDS-034  
**Document type:** Decision Support Rule Specification  
**Owner:** Jonas Solberg (Care Pathway Owner, STF-7000)  
**Approved by:** Priya Mwangi (Infection Prevention Lead, STF-5454)  
**Revision:** F  
**Effective:** 2026-06-06  

## Trigger and Action

Decision support rule supporting clinical policy CP-POL-307 and the Heart Failure Admission
and Transition pathway (CP-CHF-04).

Enforces clinical policy CP-POL-307 for pathway CP-CHF-04, alongside order set OS-CHF-23.

Trigger: an unexplained reduction in urine output over the preceding interval.

Action: present an interruptive advisory to the ordering clinician recommending that they
review the medication list against the reconciliation record. The advisory records the
response, including override and the reason given.

Override rates are monitored by the Infection Prevention Lead; a sustained rate above
threshold triggers review of the rule for alert burden.
