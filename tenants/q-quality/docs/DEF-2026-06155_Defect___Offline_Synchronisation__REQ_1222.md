<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Offline Synchronisation (REQ-1222)

**Document number:** DEF-2026-06155  
**Document type:** Defect Report  
**Owner:** Idris Solberg (Head of Quality Engineering, STF-2872)  
**Approved by:** Yusuf Sandoval (Head of Quality Engineering, STF-3600)  
**Revision:** B  
**Effective:** 2025-02-02  

## Observation and Analysis

Raised during execution of suite TS-366 against requirement REQ-1222.

Detected by suite TS-366 executing TC-1222-036 against requirement REQ-1222.

Observation: a previously entered value reappears after a session change.

Analysis: the condition arises where cached state surviving a change of authenticated user.
The covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using equivalence partitioning and
boundary value analysis so the condition is caught before system test.
