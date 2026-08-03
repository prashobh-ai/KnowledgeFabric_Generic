<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Automation Guide — Accessibility Compliance Suite

**Document number:** AFG-17  
**Document type:** Automation Framework Guide  
**Owner:** Neha Solberg (Principal Test Consultant, STF-3292)  
**Approved by:** Idris Ashgrove (Accessibility Specialist, STF-2139)  
**Revision:** C  
**Effective:** 2026-03-03  

## Structure and Conventions

Automation supporting suite TS-377 for the Accessibility Compliance capability.

Tests are written against stable selectors and are independent of execution order. Data is
provisioned by the setup fixture and cleaned down afterwards.

A test that fails intermittently is quarantined rather than retried, and raised as a defect.
Unaddressed flakiness erodes trust in the suite faster than a missing test does.

Execution reports to the automation execution grid at each pipeline run.
