<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Test Strategy — Notification Delivery

**Document number:** STRAT-15  
**Document type:** Test Strategy  
**Owner:** Jonas Castellano (Automation Lead, STF-7772)  
**Approved by:** Clara Thornbury (Product Owner, STF-5420)  
**Revision:** A  
**Effective:** 2024-01-01  

## Approach and Scope

This strategy describes how Q-Quality assures the Notification Delivery capability against
requirement REQ-1185.

The approach applies pairwise combination testing at the level where defects are cheapest to
detect, supported by exploratory testing around the areas of highest change.

Alignment: ISO/IEC/IEEE 29119-4 — test design techniques.

## Entry, Exit and Risk

Entry criteria: the build is deployed and smoke tests pass.

Exit criteria: regression suite green across two consecutive pipeline runs. Residual risk is
documented and accepted by the Product Owner.

Principal risk: concurrent updates to the same record from two sessions. Mitigation is
addressed through suite TS-355.
