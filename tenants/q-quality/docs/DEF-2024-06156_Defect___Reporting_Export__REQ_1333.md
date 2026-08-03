<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Reporting Export (REQ-1333)

**Document number:** DEF-2024-06156  
**Document type:** Defect Report  
**Owner:** Anita Achterberg (Head of Quality Engineering, STF-5844)  
**Approved by:** Omar Ferrers (Accessibility Specialist, STF-9526)  
**Revision:** C  
**Effective:** 2026-03-03  

## Observation and Analysis

Raised during execution of suite TS-399 against requirement REQ-1333.

Detected by suite TS-399 executing TC-1333-037 against requirement REQ-1333.

Observation: a previously entered value reappears after a session change.

Analysis: the condition arises where cached state surviving a change of authenticated user.
The covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using state transition testing so the
condition is caught before system test.
