<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Guest Booking Flow (REQ-1000)

**Document number:** DEF-2026-06161  
**Document type:** Defect Report  
**Owner:** Hannah Vasquez (Performance Engineer, STF-7638)  
**Approved by:** Hannah Trelawney (Performance Engineer, STF-1980)  
**Revision:** B  
**Effective:** 2025-08-08  

## Observation and Analysis

Raised during execution of suite TS-300 against requirement REQ-1000.

Detected by suite TS-300 executing TC-1000-042 against requirement REQ-1000.

Observation: a previously entered value reappears after a session change.

Analysis: the condition arises where a downstream service returning a partial response. The
covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using state transition testing so the
condition is caught before system test.
