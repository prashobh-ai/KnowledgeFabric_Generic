/* Knowledge Fabric — solution configurator rule tables.
 *
 * Rule-based, with a ready answer for every combination: the architecture,
 * the component list, the LIMITATIONS and the demo pointer are composed from
 * these tables, never invented on the fly. Options that depend on the chosen
 * cloud adapt through their `per` map (e.g. "our cloud's managed models" is
 * Azure OpenAI on Azure, Bedrock on AWS, Vertex AI on GCP); combinations that
 * cannot work are corrected by CONFLICTS — and the correction is said.
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
  aws: { label: "AWS", logo: "aws",
    boundary: "inside your AWS accounts",
    runtime:  "EKS or ECS, private subnets",
    intake:   "S3 landing + EventBridge intake",
    secrets:  "KMS + Secrets Manager" },
  azure: { label: "Azure", logo: "azure",
    boundary: "inside your Azure tenant",
    runtime:  "AKS or Container Apps, private VNet",
    intake:   "Blob landing + Event Grid intake",
    secrets:  "Key Vault + managed identities" },
  gcp: { label: "Google Cloud", logo: "gcp",
    boundary: "inside your GCP projects",
    runtime:  "GKE or Cloud Run, private VPC",
    intake:   "GCS landing + Pub/Sub intake",
    secrets:  "Cloud KMS + Secret Manager" },
  onprem: { label: "On-premises / private cloud", logo: "kubernetes",
    boundary: "inside your own data centre",
    runtime:  "Your Kubernetes (or VMware-hosted k8s)",
    intake:   "File-share watchers + queue intake",
    secrets:  "Your HSM / vault of record" },
  disconnected: { label: "Restricted / disconnected", logo: "kubernetes",
    boundary: "inside a disconnected enclave",
    runtime:  "Hardened Kubernetes, no egress",
    intake:   "Controlled-transfer batch intake",
    secrets:  "Enclave HSM; signed release bundles" },
};

/* Options whose meaning depends on the chosen cloud carry a `per` map;
   adapt() overlays the matching entry so labels and logos follow the cloud. */
function adapt(table, id, infra) {
  const base = table[id];
  if (!base) return null;
  const p = base.per && infra && base.per[infra];
  return p ? { ...base, ...p } : { ...base };
}

const IDENTITY = {
  entra:    { label: "Microsoft Entra ID", sub: "SSO from the tenant you already run", logo: "azure" },
  okta:     { label: "Okta", sub: "SAML / OIDC SSO through your Okta org", logo: "okta" },
  keycloak: { label: "Keycloak (self-hosted OIDC)", sub: "bridges your AD/LDAP, runs inside your boundary", logo: "keycloak" },
  native:   { label: "Our platform's own IAM", sub: "whatever the infrastructure provides", logo: "kubernetes",
    per: {
      aws:          { label: "AWS IAM Identity Center", sub: "SAML/OIDC federation in your accounts", logo: "aws" },
      azure:        { label: "Microsoft Entra ID", sub: "the tenant's native identity plane", logo: "azure" },
      gcp:          { label: "Google Cloud Identity", sub: "SAML/OIDC federation in your projects", logo: "gcp" },
      onprem:       { label: "Keycloak over your AD/LDAP", sub: "self-hosted OIDC, inside your boundary", logo: "keycloak" },
      disconnected: { label: "Keycloak, enclave mirror", sub: "a mirrored directory inside the enclave", logo: "keycloak" },
    } },
};

const MODELS = {
  openai: { label: "OpenAI APIs", sub: "GPT-family models over a private endpoint",
    plane: "GPT-family models over a private endpoint; provider embeddings",
    planeShort: "OpenAI models via private endpoint", badge: "OpenAI API", logos: ["openai"] },
  claude: { label: "Claude APIs (Anthropic)", sub: "Claude models over a private endpoint",
    plane: "Claude models over a private endpoint; provider embeddings",
    planeShort: "Claude via private endpoint", badge: "Claude API", logos: ["claude"] },
  managed: { label: "Our cloud's managed models", sub: "provider-hosted, inside your tenant",
    plane: "Provider-managed models deployed inside your cloud boundary",
    planeShort: "managed models, in your tenant", badge: "In-tenant managed", logos: ["kubernetes"],
    per: {
      aws:   { label: "Amazon Bedrock", sub: "Bedrock models inside your AWS accounts",
               plane: "Amazon Bedrock models inside your AWS accounts",
               planeShort: "Bedrock, in your accounts", badge: "Amazon Bedrock", logos: ["bedrock"] },
      azure: { label: "Azure OpenAI", sub: "OpenAI deployments inside your subscription",
               plane: "Azure OpenAI deployments inside your subscription",
               planeShort: "Azure OpenAI, in your tenant", badge: "Azure OpenAI", logos: ["azureai"] },
      gcp:   { label: "Vertex AI models", sub: "Gemini & partner models in your project",
               plane: "Vertex AI models inside your GCP project",
               planeShort: "Vertex AI, in your project", badge: "Vertex AI", logos: ["vertexai"] },
    } },
  selfhost: { label: "Self-hosted open models", sub: "Mistral-class open weights on your GPUs",
    plane: "Open-weight models served in-cluster on your GPU pool; local embeddings",
    planeShort: "open models on your GPU pool", badge: "Self-hosted", logos: ["ollama", "mistral", "huggingface"] },
  none: { label: "No LLM approved yet", sub: "extractive mode — verbatim quoted answers",
    plane: "Extractive mode: hybrid retrieval with verbatim quoted answers — no generation",
    planeShort: "extractive — verbatim quoted answers", badge: "Extractive only", logos: [] },
};

const VECTOR = {
  native: { label: "Our cloud's native search", sub: "the platform's managed vector service", logo: "opensearch",
    per: {
      aws:          { label: "Amazon OpenSearch", sub: "managed vector + lexical, in your accounts", logo: "opensearch" },
      azure:        { label: "Azure AI Search", sub: "managed vector + lexical, in your tenant", logo: "azure" },
      gcp:          { label: "Vertex AI Vector Search", sub: "managed vectors in your project", logo: "vertexai" },
      onprem:       { label: "OpenSearch, in-cluster", sub: "self-hosted vector + lexical", logo: "opensearch" },
      disconnected: { label: "pgvector, in-enclave", sub: "PostgreSQL-based, no external service", logo: "postgresql" },
    } },
  pgvector: { label: "PostgreSQL + pgvector", sub: "vectors beside the database you already run", logo: "postgresql" },
  redis:    { label: "Redis", sub: "in-memory vector search, lowest latency", logo: "redis" },
  pinecone: { label: "Pinecone", sub: "dedicated managed vector SaaS", logo: "pinecone" },
};

const ROLES = {
  reader:  { label: "Readers", sub: "ask questions, get cited answers", locked: true,
             ws: null },
  curator: { label: "Curators", sub: "resolve conflicts & duplicates, watch answer quality",
             ws: "Curator workbench — conflict queues" },
  admin:   { label: "Admins", sub: "route models by complexity, set caps, manage access",
             ws: "Admin console — routing & caps" },
  auditor: { label: "Auditors", sub: "evidence trails, exportable answer records",
             ws: "Auditor view — evidence & export" },
};
const ROLE_ORDER = ["reader", "curator", "admin", "auditor"];

const OBS = {
  qzotel: { label: "QualiZeal dashboards (Python + OpenTelemetry)",
    sub: "custom-built for you; the code is handed over", short: "QualiZeal OTel dashboards",
    logos: ["python", "opentelemetry"] },
  native: { label: "Our cloud's monitoring", sub: "the platform's native telemetry", short: "cloud-native monitoring",
    logos: ["kubernetes"],
    per: {
      aws:          { label: "Amazon CloudWatch", sub: "metrics, logs and traces in your accounts", short: "CloudWatch", logos: ["aws"] },
      azure:        { label: "Azure Monitor", sub: "metrics, logs and traces in your tenant", short: "Azure Monitor", logos: ["azure"] },
      gcp:          { label: "Google Cloud Monitoring", sub: "metrics, logs and traces in your project", short: "Cloud Monitoring", logos: ["gcp"] },
      onprem:       { label: "Grafana + Prometheus", sub: "self-hosted, in-cluster", short: "Grafana + Prometheus", logos: ["grafana"] },
      disconnected: { label: "Grafana, in-enclave", sub: "self-hosted, no egress", short: "Grafana, in-enclave", logos: ["grafana"] },
    } },
  datadog: { label: "Datadog", sub: "your existing Datadog org", short: "Datadog", logos: ["datadog"] },
  grafana: { label: "Grafana + Prometheus", sub: "open-source, runs inside your boundary", short: "Grafana + Prometheus", logos: ["grafana"] },
};

const SCOPES = {
  core: { label: "Grounded Q&A first",
    includes: ["Answer web app with citations & confidence", "Hybrid retrieval (lexical + semantic)",
               "Grounding gate & clarify-back", "Access scoped to the roles you chose", "Audit log"] },
  insight: { label: "Q&A + graph & knowledge health",
    includes: ["Everything in Grounded Q&A", "Entity & relationship graph",
               "Knowledge-health scoring with ranked gaps"] },
  governed: { label: "Governed platform with dashboards",
    includes: ["Everything in graph & health", "A workspace for each role you selected",
               "Usage / cost / quality telemetry on your chosen stack",
               "Model routing by question complexity, per-team caps"] },
  full: { label: "Full platform incl. API & multilingual",
    includes: ["Everything in the governed platform", "Multilingual ask-and-answer with labelled translations",
               "Answer API & embeddable widget", "BI export of telemetry"] },
};

/* Hard conflicts: the selection is adjusted and the adjustment is SAID.
   Combinations that merely change meaning (e.g. "our cloud's native search"
   on-prem) adapt through `per` maps instead — no correction needed.        */
const CONFLICTS = [
  { when: s => s.infra === "disconnected" && (s.model === "openai" || s.model === "claude"),
    force: { model: "selfhost" },
    say: "Commercial model APIs cannot be reached from a disconnected enclave — we propose self-hosted open models instead, and say so rather than pretending otherwise." },
  { when: s => s.infra === "disconnected" && s.model === "managed",
    force: { model: "selfhost" },
    say: "Cloud-managed in-tenant models need a cloud tenant — in an enclave we propose self-hosted open models instead." },
  { when: s => s.infra === "onprem" && s.model === "managed",
    force: { model: "selfhost" },
    say: "Cloud-managed models assume a cloud boundary — on your own metal we propose self-hosted open models instead." },
  { when: s => s.infra === "disconnected" && s.vector === "pinecone",
    force: { vector: "pgvector" },
    say: "Pinecone is a managed SaaS outside the enclave — we propose pgvector in-enclave instead." },
  { when: s => s.infra === "disconnected" && s.obs === "datadog",
    force: { obs: "qzotel" },
    say: "Datadog cannot receive telemetry from a no-egress enclave — we propose our Python + OpenTelemetry dashboards, running inside." },
  { when: s => s.infra === "disconnected" && (s.identity === "okta" || s.identity === "entra"),
    force: { identity: "keycloak" },
    say: "A cloud identity provider cannot be reached from a disconnected enclave — we propose Keycloak mirroring your directory inside it." },
];

/* Limitations: every rule that matches is shown, verbatim. The point is to
   call the boundaries out before a contract does.                          */
const LIMITS = [
  { when: s => s.model === "openai" || s.model === "claude",
    text: "Retrieval snippets leave your boundary to the provider endpoint. Residency follows the provider region; a provider DPA is a prerequisite, not an afterthought." },
  { when: s => s.model === "managed",
    text: "The model catalogue is limited to what your cloud provider hosts in-tenant — frontier releases arrive there later than on public APIs." },
  { when: s => s.model === "selfhost",
    text: "Answer fluency and multilingual coverage depend on the open model you approve, and GPU capacity is a hard prerequisite we size in Discover." },
  { when: s => s.model === "none",
    text: "With no LLM approved, answers are verbatim-extractive: exact quoted sentences with citations, no cross-document synthesis. The public demonstrations run exactly this mode — that is what you would get on day one." },
  { when: s => s.model === "none" && s.scope === "full",
    text: "Multilingual answering needs a generation model — it stays deferred until one is approved, however full the rest of the scope." },
  { when: s => s.vector === "pinecone" && s.infra !== "disconnected",
    text: "Pinecone holds your vectors and document chunks in its own cloud — it is the one component outside your boundary, and residency follows Pinecone's region." },
  { when: s => s.vector === "redis",
    text: "Redis keeps the vector index in memory — corpus size is bounded by RAM, which we size against your document estate in Discover." },
  { when: s => s.obs === "datadog" && s.infra !== "disconnected",
    text: "Usage and quality metrics are exported to your Datadog org — answer content stays inside your boundary; metric names and counts leave it." },
  { when: s => s.obs === "qzotel",
    text: "The QualiZeal dashboards are code we write and hand over — after Extend your team owns their upkeep, with us on support." },
  { when: s => s.roles && !s.roles.includes("curator"),
    text: "No curator role selected: conflict and duplicate queues route to admins as a weekly export. Answer quality holds longer with a named curator — we will say this again in Discover." },
  { when: s => s.roles && s.roles.some(r => r !== "reader") && (s.scope === "core" || s.scope === "insight"),
    text: "Dedicated workspaces for your selected roles arrive with the governed tier — until then those roles carry access rights but share the reader surface." },
  { when: s => s.infra === "disconnected",
    text: "No live external feeds or web retrieval inside the enclave. Platform updates arrive as signed offline bundles on your transfer cadence." },
  { when: s => s.infra === "onprem",
    text: "No managed-service acceleration: timeline is gated by your cluster, storage and GPU readiness, which we assess in week one." },
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
  s.roles = Array.isArray(s.roles) ? s.roles.slice()
          : String(s.roles || "reader").split(".").filter(r => ROLES[r]);
  if (!s.roles.includes("reader")) s.roles.unshift("reader");
  const adjustments = [];
  for (const c of CONFLICTS) {
    if (c.when(s)) { Object.assign(s, c.force); adjustments.push(c.say); }
  }
  const domain   = DOMAINS.find(d => d.id === s.domain) || DOMAINS[DOMAINS.length - 1];
  const infra    = INFRA[s.infra];
  const identity = adapt(IDENTITY, s.identity, s.infra);
  const model    = adapt(MODELS, s.model, s.infra);
  const vector   = adapt(VECTOR, s.vector, s.infra);
  const obs      = adapt(OBS, s.obs, s.infra);
  const roles    = ROLE_ORDER.filter(r => s.roles.includes(r)).map(r => ({ id: r, ...ROLES[r] }));
  const scope    = SCOPES[s.scope];
  const limits   = LIMITS.filter(l => l.when(s)).map(l => l.text);
  const phases   = (s.infra === "onprem" || s.infra === "disconnected")
    ? PHASES.heavy : PHASES.standard;
  return { sel: s, domain, infra, identity, model, vector, obs, roles, scope, limits, adjustments, phases };
}
