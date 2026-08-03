<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Automation Guide — Loyalty Accrual Suite

**Document number:** AFG-20  
**Document type:** Automation Framework Guide  
**Owner:** Amara Delacroix (Principal Test Consultant, STF-2483)  
**Approved by:** Neha Haverford (Release Manager, STF-6133)  
**Revision:** F  
**Effective:** 2026-06-06  

## Structure and Conventions

Automation supporting suite TS-322 for the Loyalty Accrual capability.

Tests are written against stable selectors and are independent of execution order. Data is
provisioned by the setup fixture and cleaned down afterwards.

A test that fails intermittently is quarantined rather than retried, and raised as a defect.
Unaddressed flakiness erodes trust in the suite faster than a missing test does.

Execution reports to the test management tool at each pipeline run.
