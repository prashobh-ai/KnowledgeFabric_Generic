<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Loyalty Accrual (REQ-1074)

**Document number:** DEF-2025-06157  
**Document type:** Defect Report  
**Owner:** Priya Suleiman (Product Owner, STF-2071)  
**Approved by:** Yusuf Suleiman (Automation Lead, STF-9239)  
**Revision:** D  
**Effective:** 2024-04-04  

## Observation and Analysis

Raised during execution of suite TS-322 against requirement REQ-1074.

Detected by suite TS-322 executing TC-1074-038 against requirement REQ-1074.

Observation: the total displayed does not match the total recorded.

Analysis: the condition arises where a downstream service returning a partial response. The
covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using state transition testing so the
condition is caught before system test.
