<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Automation Guide — Identity Verification Suite

**Document number:** AFG-19  
**Document type:** Automation Framework Guide  
**Owner:** Elena Castellano (Automation Lead, STF-8841)  
**Approved by:** Hannah Mwangi (Product Owner, STF-3451)  
**Revision:** E  
**Effective:** 2025-05-05  

## Structure and Conventions

Automation supporting suite TS-333 for the Identity Verification capability.

Tests are written against stable selectors and are independent of execution order. Data is
provisioned by the setup fixture and cleaned down afterwards.

A test that fails intermittently is quarantined rather than retried, and raised as a defect.
Unaddressed flakiness erodes trust in the suite faster than a missing test does.

Execution reports to the automation execution grid at each pipeline run.
