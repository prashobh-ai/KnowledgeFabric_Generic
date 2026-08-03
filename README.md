<h1 align="center">Knowledge Fabric</h1>
<p align="center"><strong>Every answer, traced to its source.</strong></p>
<p align="center">
A multi-tenant demonstration platform — QualiZeal AI Center of Excellence.
</p>

---

## What this is

A **demo factory**. Eleven pre-built tenants across nine industry subtypes, each
with its own synthetic corpus, brand, domain vocabulary and question set. The
demonstration exists before the prospect does.

```
python -m pipeline.build_tenants     # 11 tenants, 637 documents, ~30 seconds
```

## The problem it solves

A knowledge fabric built for one airline did not transfer to the next airline,
because the second carrier's documents were a different shape entirely. The same
trap exists inside every vertical:

| Both are "Healthcare" | Q-Health (provider) | Q-Assure Claims (payer) |
|---|---|---|
| Documents | care pathways, order sets, clinical policy | medical policy, denials, appeals |
| Codes | SNOMED, LOINC, ICD-10-CM | CPT/HCPCS, MS-DRG |
| Standards | HL7 FHIR | X12 837 / 835 / 270 / 271 |
| Regulator hooks | Conditions of Participation | claims and appeals procedure rules |
| **Vocabulary overlap** | **23.8%** — and most of that is common English | |

**The unit of reuse is the subtype, not the industry.** Configuring "healthcare"
once and reusing it guarantees one of those two tenants is wrong. The registry
treats them as separate builds, deliberately.

## Tenants

| Tenant | Industry | Subtype |
|---|---|---|
| Q-Airlines | Aviation | Airline operations & continuing airworthiness |
| Q-AeroTech | Aviation | MRO & component overhaul |
| Q-Health | Healthcare | Provider / clinical (EMR) |
| Q-Assure Claims | Healthcare | Payer / claims & revenue cycle |
| Q-Pharma | Life Sciences | Clinical development & GxP |
| Q-MediTech | Medical Devices | Manufacturer / QMS |
| Q-Bank | Financial Services | Retail & commercial banking |
| Q-Assurance | Insurance | Carrier / underwriting & claims |
| Q-Cruise | Cruise & Maritime | Cruise line operations |
| Q-Retail | Retail & Consumer | Omnichannel retail operations |
| Q-Quality | Quality Engineering | Testing & QA services |

## Everything is synthetic

No client name, document, or dataset appears anywhere in this repository. Every
organisation, identifier, person, date and finding is invented. Each generated
file carries a banner saying so.

Domain *structure* — which documents exist, what they are called, which
identifiers thread through them, which regulations bite — follows public
standards and regulator sources. That is what makes a document read correctly to
a practitioner while remaining safe to publish, screenshot and hand out.

A safety scan runs in CI and fails the build if a known real-world name appears.

## The property that makes the graph work

Public corpora are the wrong shape for this demo: inconsistent, unevenly
licensed, and — fatally — they do not cross-reference each other. A knowledge
graph has nothing to bridge if every document is about something different.

Generated corpora let us guarantee the one property the demo depends on: **the
same identifier appears in documents of different types**, written in different
registers by different notional authors.

| Tenant | Spine identifier | Document types each value appears in |
|---|---|---|
| Q-Airlines | aircraft registration | 7.1 |
| Q-AeroTech | aircraft registration | 6.9 |
| Q-MediTech | device model | 5.7 |
| Q-Pharma | study identifier | 5.5 |
| Q-Assurance | policy form number | 5.4 |
| Q-Cruise | vessel | 5.1 |
| Q-Quality | requirement identifier | 4.8 |
| Q-Health | care pathway | 4.6 |
| Q-Assure Claims | medical policy number | 4.3 |
| Q-Bank | regulatory obligation | 4.3 |
| Q-Retail | article number | 3.6 |

An Airworthiness Directive names an applicability; a task card closes it against
a tail; a technical log records the defect that triggered it. Same registration,
three document types, three registers. That is a real cross-document link, not a
coincidental keyword overlap.

## Determinism

Everything derives from one seed in `tenants/registry.yml`. Two builds produce
byte-identical corpora. A demo shown on Tuesday is the demo shown on Friday, and
a regression in retrieval is never confused with a change in the data.

## Adding a tenant

Adding a *subtype* means a new domain pack — roughly 200 lines of data
declaring spine identifiers, document types and vocabulary. Adding a *tenant* in
an existing subtype means an entry in the registry:

```yaml
- slug: q-newco
  name: Q-NewCo
  industry: Aviation
  subtype: MRO & Component Overhaul
  accent: "#1F4E8C"
  logo: wrench
  corpus: { generator: aviation, profile: mro, documents: 58 }
```

Re-badging for a real prospect: change `name`, `accent` and `logo`, drop their
documents into `tenants/<slug>/docs/`, rebuild.

## Layout

```
tenants/
  registry.yml              every tenant, one file
  <slug>/
    docs/                   generated synthetic corpus
    brand/logo.svg          generated mark
    tenant.json             resolved configuration
    questions.json          seeded demo questions
pipeline/
  synth/
    engine.py               generation engine, domain-agnostic
    pack_aviation.py        reference pack — operator & MRO
    pack_healthcare_*.py    reference pair — the subtype proof
    packs_extra.py          pharma, devices, banking, insurance,
                            maritime, retail, quality
  build_tenants.py          orchestrator
```
