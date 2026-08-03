<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Accessibility Compliance (REQ-1259)

**Document number:** DEF-2025-06160  
**Document type:** Defect Report  
**Owner:** Karl Ravensworth (Release Manager, STF-7903)  
**Approved by:** Neha Delacroix (Release Manager, STF-4237)  
**Revision:** A  
**Effective:** 2024-07-07  

## Observation and Analysis

Raised during execution of suite TS-377 against requirement REQ-1259.

Detected by suite TS-377 executing TC-1259-041 against requirement REQ-1259.

Observation: a previously entered value reappears after a session change.

Analysis: the condition arises where an interrupted network during a multi-step submission.
The covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using equivalence partitioning and
boundary value analysis so the condition is caught before system test.
