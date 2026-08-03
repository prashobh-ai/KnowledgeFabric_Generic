<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Adjudication Edit — Physical Therapy Visit Limits (97110)

**Document number:** EDIT-97110-26  
**Document type:** Adjudication Edit Specification  
**Owner:** Farah Ravensworth (Medical Policy Director, STF-5340)  
**Approved by:** Mei Solberg (Payment Integrity Lead, STF-5709)  
**Revision:** C  
**Effective:** 2026-03-03  

## Trigger and Disposition

Adjudication edit supporting medical policy MP-1033 (Physical Therapy Visit Limits).

Implements medical policy MP-1033 in adjudication.

Trigger: a claim line containing procedure code 97110 where the submitted documentation or
authorisation record does not evidence the ordering provider holding the required specialty
designation.

Disposition: suspend the line for clinical review. On review, if the requested frequency
exceeds the limit stated in the policy, the line denies with the corresponding remark code.

Configured in the provider portal by the Medical Policy Director. Edit performance is
monitored through the first-pass adjudication rate for claims in this policy family.
