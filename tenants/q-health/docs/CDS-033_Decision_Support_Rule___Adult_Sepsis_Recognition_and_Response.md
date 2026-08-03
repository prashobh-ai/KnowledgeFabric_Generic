<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Decision Support Rule — Adult Sepsis Recognition and Response

**Document number:** CDS-033  
**Document type:** Decision Support Rule Specification  
**Owner:** Anders Bertrand (Infection Prevention Lead, STF-6970)  
**Approved by:** Hannah Okonjo (Clinical Informatics Lead, STF-3822)  
**Revision:** E  
**Effective:** 2025-05-05  

## Trigger and Action

Decision support rule supporting clinical policy CP-POL-300 and the Adult Sepsis Recognition
and Response pathway (CP-SEPSIS-01).

Enforces clinical policy CP-POL-300 for pathway CP-SEPSIS-01, alongside order set OS-
SEPSIS-18.

Trigger: an unexplained reduction in urine output over the preceding interval.

Action: present an interruptive advisory to the ordering clinician recommending that they
refer to the specialist team using the standard referral pathway. The advisory records the
response, including override and the reason given.

Override rates are monitored by the Clinical Informatics Lead; a sustained rate above
threshold triggers review of the rule for alert burden.
