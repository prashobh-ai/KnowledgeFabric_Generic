<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Search and Filter (REQ-1148)

**Document number:** DEF-2024-06159  
**Document type:** Defect Report  
**Owner:** Ravi Sandoval (Automation Lead, STF-4315)  
**Approved by:** Mei Vasquez (Product Owner, STF-8159)  
**Revision:** F  
**Effective:** 2026-06-06  

## Observation and Analysis

Raised during execution of suite TS-344 against requirement REQ-1148.

Detected by suite TS-344 executing TC-1148-040 against requirement REQ-1148.

Observation: the total displayed does not match the total recorded.

Analysis: the condition arises where cached state surviving a change of authenticated user.
The covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using risk-based exploratory charters
so the condition is caught before system test.
