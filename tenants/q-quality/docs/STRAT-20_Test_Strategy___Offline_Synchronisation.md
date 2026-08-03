<!--
SYNTHETIC DOCUMENT — NOT A REAL RECORD

Generated for product demonstration. Every organisation, identifier, person,
date and finding in this file is fictional. No customer document, dataset or
confidential material was used to produce it. Domain structure and terminology
follow public standards and regulator sources so that the document reads
correctly to a practitioner; the content itself is invented.
-->

# Test Strategy — Offline Synchronisation

**Document number:** STRAT-20  
**Document type:** Test Strategy  
**Owner:** Nikhil Castellano (Product Owner, STF-9539)  
**Approved by:** Elena Mwangi (Product Owner, STF-1098)  
**Revision:** F  
**Effective:** 2026-06-06  

## Approach and Scope

This strategy describes how Q-Quality assures the Offline Synchronisation capability against
requirement REQ-1222.

The approach applies decision table testing at the level where defects are cheapest to
detect, supported by exploratory testing around the areas of highest change.

Alignment: ISO/IEC/IEEE 29119-3 — test documentation templates and content.

## Entry, Exit and Risk

Entry criteria: the build is deployed and smoke tests pass.

Exit criteria: coverage of the agreed scope achieved with residual risk documented. Residual
risk is documented and accepted by the Product Owner.

Principal risk: locale and time-zone handling at the day boundary. Mitigation is addressed
through suite TS-366.
