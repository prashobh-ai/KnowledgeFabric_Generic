<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Automation Guide — Search and Filter Suite

**Document number:** AFG-16  
**Document type:** Automation Framework Guide  
**Owner:** Priya Rahimi (Performance Engineer, STF-3360)  
**Approved by:** Ingrid Eriksen (Product Owner, STF-7327)  
**Revision:** B  
**Effective:** 2025-02-02  

## Structure and Conventions

Automation supporting suite TS-344 for the Search and Filter capability.

Tests are written against stable selectors and are independent of execution order. Data is
provisioned by the setup fixture and cleaned down afterwards.

A test that fails intermittently is quarantined rather than retried, and raised as a defect.
Unaddressed flakiness erodes trust in the suite faster than a missing test does.

Execution reports to the defect tracker at each pipeline run.
