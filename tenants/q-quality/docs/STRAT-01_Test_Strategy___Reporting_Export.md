<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Test Strategy — Reporting Export

**Document number:** STRAT-01  
**Document type:** Test Strategy  
**Owner:** Yusuf Eriksen (Performance Engineer, STF-2352)  
**Approved by:** Tomas Warden (Release Manager, STF-7277)  
**Revision:** A  
**Effective:** 2024-07-07  

## Approach and Scope

This strategy describes how Q-Quality assures the Reporting Export capability against
requirement REQ-1333.

The approach applies equivalence partitioning and boundary value analysis at the level where
defects are cheapest to detect, supported by exploratory testing around the areas of highest
change.

Alignment: ISO/IEC 25010 — product quality characteristics and sub-characteristics.

## Entry, Exit and Risk

Entry criteria: the build is deployed and smoke tests pass.

Exit criteria: coverage of the agreed scope achieved with residual risk documented. Residual
risk is documented and accepted by the Release Manager.

Principal risk: an interrupted network during a multi-step submission. Mitigation is
addressed through suite TS-399.
