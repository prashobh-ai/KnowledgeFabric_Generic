<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Automation Guide — Guest Booking Flow Suite

**Document number:** AFG-18  
**Document type:** Automation Framework Guide  
**Owner:** Jonas Haverford (Release Manager, STF-7138)  
**Approved by:** Tomas Delacroix (Product Owner, STF-5092)  
**Revision:** D  
**Effective:** 2024-04-04  

## Structure and Conventions

Automation supporting suite TS-300 for the Guest Booking Flow capability.

Tests are written against stable selectors and are independent of execution order. Data is
provisioned by the setup fixture and cleaned down afterwards.

A test that fails intermittently is quarantined rather than retried, and raised as a defect.
Unaddressed flakiness erodes trust in the suite faster than a missing test does.

Execution reports to the pipeline reporting dashboard at each pipeline run.
