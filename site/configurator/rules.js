/* Knowledge Fabric — solution configurator rule tables.
 *
 * This is a rule-based show with a ready answer for every combination: the
 * architecture, the component list, the LIMITATIONS and the demo pointer are
 * all composed from these tables, never invented on the fly. 5 infrastructures
 * x 4 model postures x 4 scopes x 12 domains — every path resolves.
 *
 * Editing: change a row here, refresh. Nothing else knows the content.
 */
"use strict";

const DOMAINS = [
  { id: "q-airlines",      label: "Airline operations",            demo: "q-airlines",
    built: "a network carrier's fabric threading tail numbers across maintenance, operations and safety records" },
  { id: "q-aerotech",      label: "Aerospace MRO",                 demo: "q-aerotech",
    built: "an MRO fabric where the ATA chapter links manuals, task cards and findings end to end" },
  { id: "q-health",        label: "Healthcare provider",           demo: "q-health",
    built: "a provider fabric linking care pathways to the policies and order sets that implement them" },
  { id: "q-assure-claims", label: "Health plan / payer",           demo: "q-assure-claims",
    built: "a payer fabric tracing every denial reason to the medical policy clause behind it" },
  { id: "q-pharma",        label: "Pharma / GxP",                  demo: "q-pharma",
    built: "a GxP fabric chaining deviation to CAPA to SOP revision under Part 11 evidence" },
  { id: "q-devicelab",     label: "Medical devices / QMS",         demo: "q-devicelab",
    built: "a device-QMS fabric running complaint to investigation to reportability decision" },
  { id: "q-bank",          label: "Banking & financial services",  demo: "q-bank",
    built: "a banking fabric mapping regulatory obligations to the internal controls that satisfy them" },
  { id: "q-assurance",     label: "Insurance / audit & assurance", demo: "q-assurance",
    built: "an assurance fabric reconciling policy wording clauses with claims handling instructions" },
  { id: "q-cruise",        label: "Maritime & cruise operations",  demo: "q-cruise",
    built: "a marine-operations fabric linking safety management procedures to inspection findings" },
  { id: "q-retail",        label: "Retail & supply chain",         demo: "q-retail",
    built: "a retail fabric tracing vendor requirements to the product specifications that fail them" },
  { id: "q-quality",       label: "Software & QA services",        demo: "q-quality",
    built: "a QA fabric tracing requirement through test case to defect and back — our own discipline, on itself" },
  { id: "other",           label: "Another regulated domain",      demo: "q-quality",
    built: "eleven regulated-industry fabrics on the same platform — the scaffolding transfers even when the industry label differs" },
];

const INFRA = {
  aws: { label: "AWS",
    boundary: "inside your AWS accounts",
    identity: "Your existing IdP via IAM Identity Center (SAML/OIDC)",
    runtime:  "EKS or ECS, private subnets",
    intake:   "S3 landing + EventBridge intake",
    search:   "OpenSearch / pgvector on RDS",
    secrets:  "KMS + Secrets Manager",
  },
  azure: { label: "Azure",
    boundary: "inside your Azure tenant",
    identity: "Microsoft Entra ID (your existing tenant)",
    runtime:  "AKS or Container Apps, private VNet",
    intake:   "Blob landing + Event Grid intake",
    search:   "Azure AI Search / pgvector on Flexible Server",
    secrets:  "Key Vault + managed identities",
  },
  gcp: { label: "Google Cloud",
    boundary: "inside your GCP projects",
    identity: "Your existing IdP via Cloud Identity (SAML/OIDC)",
    runtime:  "GKE or Cloud Run, private VPC",
    intake:   "GCS landing + Pub/Sub intake",
    search:   "Vertex AI Vector Search / AlloyDB pgvector",
    secrets:  "Cloud KMS + Secret Manager",
  },
  onprem: { label: "On-premises / private cloud",
    boundary: "inside your own data centre",
    identity: "Your AD/LDAP through an OIDC bridge (e.g. Keycloak)",
    runtime:  "Your Kubernetes (or VMware-hosted k8s)",
    intake:   "File-share watchers + message queue intake",
    search:   "OpenSearch / pgvector, in-cluster",
    secrets:  "Your HSM/vault of record",
  },
  disconnected: { label: "Restricted / disconnected",
    boundary: "inside a disconnected enclave",
    identity: "Enclave identity mirror of your directory",
    runtime:  "Hardened Kubernetes, no egress",
    intake:   "Controlled-transfer batch intake",
    search:   "pgvector, in-enclave",
    secrets:  "Enclave HSM; signed release bundles",
  },
};

const MODELS = {
  api: { label: "Commercial model APIs are approved",
    plane: "Frontier commercial models over a private endpoint; provider embeddings",
    planeShort: "frontier models via private endpoint",
    badge: "Commercial API",
  },
  intenant: { label: "Cloud-managed models inside our tenant",
    plane: "Provider-managed models deployed inside your cloud boundary",
    planeShort: "provider-managed models, in your tenant",
    badge: "In-tenant managed",
  },
  selfhost: { label: "Only self-hosted open models",
    plane: "Open-weight models served in-cluster on your GPU pool; local embeddings",
    planeShort: "open models on your GPU pool",
    badge: "Self-hosted",
  },
  none: { label: "No LLM approved yet",
    plane: "Extractive mode: hybrid retrieval with verbatim quoted answers — no generation",
    planeShort: "extractive — verbatim quoted answers",
    badge: "Extractive only",
  },
};

const SCOPES = {
  core: { label: "Grounded Q&A first",
    includes: ["Answer web app with citations & confidence", "Hybrid retrieval (lexical + semantic)",
               "Grounding gate & clarify-back", "Role-scoped access", "Audit log"],
  },
  insight: { label: "Q&A + graph & knowledge health",
    includes: ["Everything in Grounded Q&A", "Entity & relationship graph",
               "Knowledge-health scoring with ranked gaps"],
  },
  governed: { label: "Governed platform with dashboards",
    includes: ["Everything in graph & health", "Curator workbench & answer-monitoring dashboard",
               "Usage / cost / quality telemetry", "Admin console: route models by question complexity, set caps"],
  },
  full: { label: "Full platform incl. API & multilingual",
    includes: ["Everything in the governed platform", "Multilingual ask-and-answer with labelled translations",
               "Answer API & embeddable widget", "BI export of telemetry"],
  },
};

/* Hard conflicts: the selection is adjusted and the adjustment is SAID.   */
const CONFLICTS = [
  { when: s => s.infra === "disconnected" && s.model === "api",
    force: { model: "selfhost" },
    say: "Commercial model APIs cannot be reached from a disconnected enclave — we propose self-hosted open models instead, and say so rather than pretending otherwise." },
  { when: s => s.infra === "disconnected" && s.model === "intenant",
    force: { model: "selfhost" },
    say: "Cloud-managed in-tenant models need a cloud tenant — in an enclave we propose self-hosted open models instead." },
  { when: s => s.infra === "onprem" && s.model === "intenant",
    force: { model: "selfhost" },
    say: "Cloud-managed models assume a cloud boundary — on your own metal we propose self-hosted open models instead." },
];

/* Limitations: every rule that matches is shown, verbatim. The point is to
   call the boundaries out before a contract does.                          */
const LIMITS = [
  { when: s => s.model === "api",
    text: "Retrieval snippets leave your boundary to the provider endpoint. Residency follows the provider region; a provider DPA is a prerequisite, not an afterthought." },
  { when: s => s.model === "intenant",
    text: "The model catalogue is limited to what your cloud provider hosts in-tenant — frontier releases arrive there later than on public APIs." },
  { when: s => s.model === "selfhost",
    text: "Answer fluency and multilingual coverage depend on the open model you approve, and GPU capacity is a hard prerequisite we size in Discover." },
  { when: s => s.model === "none",
    text: "With no LLM approved, answers are verbatim-extractive: exact quoted sentences with citations, no cross-document synthesis. The public demonstrations run exactly this mode — that is what you would get on day one." },
  { when: s => s.model === "none" && (s.scope === "full"),
    text: "Multilingual answering needs a generation model — it stays deferred until one is approved, however full the rest of the scope." },
  { when: s => s.infra === "disconnected",
    text: "No live external feeds or web retrieval inside the enclave. Platform updates arrive as signed offline bundles on your transfer cadence." },
  { when: s => s.infra === "onprem",
    text: "No managed-service acceleration: timeline is gated by your cluster, storage and GPU readiness, which we assess in week one." },
  { when: s => s.scope === "core",
    text: "First release ships no curator dashboard — conflict and duplicate queues arrive as a weekly export until the governed tier." },
  { when: s => s.scope === "core" || s.scope === "insight",
    text: "Model governance (routing by complexity, per-team caps) is not in this tier — one default model serves all questions." },
  { when: s => s.scope === "full" && s.model === "selfhost",
    text: "Answer-API latency under load depends on your GPU pool; we publish the measured envelope in Prove rather than promising one now." },
];

const PHASES = {
  standard:  [["Discover", "weeks"], ["Prove", "weeks"], ["Harden", "weeks"], ["Extend", "ongoing"]],
  heavy:     [["Discover", "weeks"], ["Prove", "weeks"], ["Harden", "longer — boundary work"], ["Extend", "ongoing"]],
};

function resolve(sel) {
  const s = { ...sel };
  const adjustments = [];
  for (const c of CONFLICTS) {
    if (c.when(s)) { Object.assign(s, c.force); adjustments.push(c.say); }
  }
  const domain = DOMAINS.find(d => d.id === s.domain) || DOMAINS[DOMAINS.length - 1];
  const infra  = INFRA[s.infra];
  const model  = MODELS[s.model];
  const scope  = SCOPES[s.scope];
  const limits = LIMITS.filter(l => l.when(s)).map(l => l.text);
  const phases = (s.infra === "onprem" || s.infra === "disconnected")
    ? PHASES.heavy : PHASES.standard;
  return { sel: s, domain, infra, model, scope, limits, adjustments, phases };
}
