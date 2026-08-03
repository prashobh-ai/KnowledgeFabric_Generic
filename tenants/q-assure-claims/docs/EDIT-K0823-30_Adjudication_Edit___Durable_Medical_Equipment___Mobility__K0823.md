<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Adjudication Edit — Durable Medical Equipment — Mobility (K0823)

**Document number:** EDIT-K0823-30  
**Document type:** Adjudication Edit Specification  
**Owner:** Anders Lindqvist (Clinical Reviewer, STF-6303)  
**Approved by:** Priya Ashgrove (Payment Integrity Lead, STF-3646)  
**Revision:** A  
**Effective:** 2024-07-07  

## Trigger and Disposition

Adjudication edit supporting medical policy MP-0819 (Durable Medical Equipment — Mobility).

Implements medical policy MP-0819 in adjudication.

Trigger: a claim line containing procedure code K0823 where the submitted documentation or
authorisation record does not evidence the absence of a contraindication recorded in the
submitted notes.

Disposition: suspend the line for clinical review. On review, if the member was not eligible
on the date of service, the line denies with the corresponding remark code.

Configured in the clearinghouse gateway by the Clinical Reviewer. Edit performance is
monitored through the proportion of denials citing insufficient documentation.
