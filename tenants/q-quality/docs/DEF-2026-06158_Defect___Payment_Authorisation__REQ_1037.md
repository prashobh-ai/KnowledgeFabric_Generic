<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Payment Authorisation (REQ-1037)

**Document number:** DEF-2026-06158  
**Document type:** Defect Report  
**Owner:** Nikhil Thornbury (Product Owner, STF-3800)  
**Approved by:** Neha Marchetti (Accessibility Specialist, STF-8034)  
**Revision:** E  
**Effective:** 2025-05-05  

## Observation and Analysis

Raised during execution of suite TS-311 against requirement REQ-1037.

Detected by suite TS-311 executing TC-1037-039 against requirement REQ-1037.

Observation: a previously entered value reappears after a session change.

Analysis: the condition arises where a downstream service returning a partial response. The
covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using decision table testing so the
condition is caught before system test.
