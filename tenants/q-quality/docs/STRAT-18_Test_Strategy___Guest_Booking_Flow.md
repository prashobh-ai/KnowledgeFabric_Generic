<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Test Strategy — Guest Booking Flow

**Document number:** STRAT-18  
**Document type:** Test Strategy  
**Owner:** Tomas Warden (Product Owner, STF-6509)  
**Approved by:** Priya Solberg (Performance Engineer, STF-3670)  
**Revision:** D  
**Effective:** 2024-04-04  

## Approach and Scope

This strategy describes how Q-Quality assures the Guest Booking Flow capability against
requirement REQ-1000.

The approach applies state transition testing at the level where defects are cheapest to
detect, supported by exploratory testing around the areas of highest change.

Alignment: ISO/IEC/IEEE 29119-3 — test documentation templates and content.

## Entry, Exit and Risk

Entry criteria: the build is deployed and smoke tests pass.

Exit criteria: all planned cases executed with no open severity-one defects. Residual risk
is documented and accepted by the Performance Engineer.

Principal risk: cached state surviving a change of authenticated user. Mitigation is
addressed through suite TS-300.
