<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Companion Guide — Claim Submission for Durable Medical Equipment — Mobility

**Document number:** CG-0819  
**Document type:** EDI Companion Guide Section  
**Owner:** Idris Eriksen (Configuration Analyst, STF-1478)  
**Approved by:** Pieter Sandoval (Clinical Reviewer, STF-9332)  
**Revision:** C  
**Effective:** 2026-03-03  

## Submission Requirements

This companion guide describes Q-Assure Claims requirements for electronic submission of
claims subject to medical policy MP-0819.

Claims for procedure code K0823 must be submitted using the professional or institutional
claim transaction as applicable. Remittance is returned on the corresponding remittance
advice transaction.

Eligibility should be verified using the eligibility inquiry and response transaction pair
before the service is rendered; a claim submitted for an ineligible member will deny.

Transaction standards are adopted under 42 CFR 405.926. Submissions that fail structural
validation are rejected at the edit and audit rules engine before adjudication.
