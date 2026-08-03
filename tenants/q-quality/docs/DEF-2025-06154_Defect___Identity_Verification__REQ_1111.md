<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Defect — Identity Verification (REQ-1111)

**Document number:** DEF-2025-06154  
**Document type:** Defect Report  
**Owner:** Farah Ravensworth (Head of Quality Engineering, STF-3705)  
**Approved by:** Nikhil Rahimi (Principal Test Consultant, STF-6159)  
**Revision:** A  
**Effective:** 2024-01-01  

## Observation and Analysis

Raised during execution of suite TS-333 against requirement REQ-1111.

Detected by suite TS-333 executing TC-1111-035 against requirement REQ-1111.

Observation: the total displayed does not match the total recorded.

Analysis: the condition arises where concurrent updates to the same record from two
sessions. The covering test case detected the condition, but earlier stages did not.

Recommendation: strengthen coverage at the lower level using decision table testing so the
condition is caught before system test.
