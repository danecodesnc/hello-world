# Interview Guide — Agentic AI Support Portfolio

This guide is written for Dane to study. It assumes strong Technical Support/API troubleshooting experience and newer hands-on experience with modern agentic-AI architecture.

## 30-second explanation

> I modernized the Technical Support and API troubleshooting work I already know by building a Python-based agentic support portfolio. The system gathers synthetic evidence through controlled tools, classifies an issue, applies deterministic escalation guardrails, exposes REST endpoints through FastAPI, and stops for human review when risk is high or a diagnostic tool fails. I also built and verified an n8n orchestration workflow in CI. There is an optional OpenAI Responses API tool-calling path with context limits and token/latency telemetry, but I keep real external-provider verification separate until a credential-backed run passes.

## 2-minute explanation

> The main project is a support-investigation agent. A user gives it a synthetic support ticket, such as a 401 after credential rotation. The application first bounds the input, then gathers approved evidence from a synthetic knowledge base, customer context, service status, and logs. It classifies the problem and produces structured troubleshooting steps and a confidence score.
>
> I deliberately separated probabilistic AI behavior from deterministic policy. P1/high-risk conditions and diagnostic-tool failures force human review through Python rules rather than trusting an LLM alone. The demo also has an approve/reject/escalate human-decision step, but it never writes to Jira, Slack, a CRM, or a customer system.
>
> The same logic is exposed through FastAPI so it can be exercised like a real service from Postman. The optional live path uses the OpenAI Responses API with allow-listed function tools, bounded tool rounds, bounded context, retry/timeout controls, and provider token telemetry. Separately, I built an n8n incident-routing workflow and a GitHub Actions job that launches the official n8n container, imports the workflow, executes it, and verifies the result. I used only synthetic data so I can demonstrate the complete architecture safely.

## Architecture in plain English

Think of the system like a careful senior support engineer with a restricted toolbox:

1. **User/Event** — a support problem arrives.
2. **Application/API** — Streamlit or FastAPI receives and validates it.
3. **Agent** — decides what evidence is relevant.
4. **Tools** — only approved synthetic lookups are available.
5. **Observations** — tool results become evidence.
6. **Decision** — the workflow classifies the issue and builds a troubleshooting recommendation.
7. **Guardrails** — deterministic Python checks risk, failures, and execution limits.
8. **Human approval** — high-risk paths stop for approve/reject/escalate review.
9. **Observability** — the run exposes tools, timing, limits, token information, and action status.

See `ARCHITECTURE.md` for the diagram and technical boundaries.

## Why this is an agent rather than merely a chatbot

A chatbot mainly receives text and returns text. The optional live agent can request an approved tool, receive the tool result, incorporate that observation, request another tool if needed, and continue until it produces a final answer or reaches its tool-round limit.

The public offline mode mirrors the same support-investigation architecture deterministically so interviews do not depend on network access or a paid API credential.

## Where the LLM is used — and where it is intentionally not used

### LLM responsibility in optional live mode

- interpret natural-language support context;
- decide which allow-listed tool to request;
- synthesize tool evidence into a concise explanation.

### LLM is intentionally **not** the sole authority for

- P1/high-risk escalation policy;
- tool allow-list enforcement;
- maximum execution rounds;
- input/context limits;
- external-write authorization;
- human approval;
- secret handling.

Those belong to deterministic Python/application controls.

## What Python does

Python is the control layer. It handles:

- request validation and limits;
- evidence retrieval;
- classification logic;
- deterministic guardrails;
- tool execution;
- human-decision records;
- telemetry;
- REST endpoints;
- tests;
- provider client configuration.

## APIs

`api.py` exposes the portfolio through FastAPI/OpenAPI. It demonstrates the same type of request/response behavior I used to troubleshoot in customer-facing SaaS work.

Primary endpoints:

- `GET /health`
- `POST /agent/investigate`
- `POST /incident/route`
- `POST /incident/decision`
- `POST /api/diagnose`

The optional live agent also demonstrates calling an LLM provider API through the OpenAI SDK.

## n8n

n8n is the orchestration layer. Conceptually it represents:

```text
Trigger
  ↓
Normalize event
  ↓
Classify
  ↓
Deterministic guardrail
  ↓
Human-routing decision
  ↓
Verification / downstream step
```

The repository does more than store an n8n JSON file: GitHub Actions launches the official n8n container, imports the verification workflow, executes it, and requires the expected PASS output.

## Token controls — simple analogy

Think of the model context like a meeting room with limited seats.

- **Tokens** are roughly the pieces of text occupying those seats.
- **Context** is everything brought into the room for the current model call.
- **Input tokens** are what I send to the model.
- **Output tokens** are what the model generates.
- **Cached tokens**, when reported by the provider, represent reusable input processing.
- **Cost** generally grows with token usage, but pricing changes, so the portfolio does not hard-code model rates.

Controls in the project include ticket-size limits, an approximate preflight input-token budget, bounded evidence, maximum live context items, maximum tool rounds, and maximum output tokens.

Offline token counts are explicitly labeled as rough local estimates. Live provider counts are recorded separately when the API returns them.

## Guardrails

The portfolio demonstrates several guardrail types:

- allow-listed tools only;
- strict tool JSON schemas;
- bounded input/context/tool rounds/output;
- deterministic P1/high-risk checks;
- diagnostic-tool failure → human review;
- preview-only escalation;
- no enabled external writes;
- synthetic public data;
- bounded public API error messages.

## Human in the loop

If a high-risk event is detected, the workflow does not act autonomously. The Streamlit demo presents **Approve**, **Reject**, and **Escalate** choices. The selected decision is recorded, but the result still states `external_action_taken: false`.

The point is to demonstrate that agent autonomy should have boundaries.

## Monitoring / observability

Offline mode records:

- request ID;
- approximate input-token estimate;
- context/evidence item count;
- tools used;
- guardrails triggered;
- decision trace;
- latency;
- action status.

Optional live mode adds:

- model;
- provider input/output/total tokens;
- cached tokens when available;
- tool events and durations;
- context-document count;
- configured-rate cost estimate when rates are supplied.

## Failure handling

Examples:

- too-short API input → validation error;
- missing live API key → live mode is blocked;
- live provider exception → bounded 502 response rather than raw internals;
- malformed tool call → safe tool-error record;
- synthetic diagnostic-tool failure → human review;
- tool-round limit reached → bounded termination message;
- ambiguous evidence → lower-confidence recommendation rather than a fabricated precise cause.

## Security

The public repository uses synthetic data, environment-variable secrets, a tool allow-list, context/execution limits, and zero external-write capability. These are portfolio safety controls—not a claim of production security certification.

See `SECURITY.md` for the full boundary.

## Testing

The regression suite covers support classification, high-risk policy, tool-failure routing, telemetry, FastAPI endpoints, API input validation, human approval, API diagnostics, and the mocked LLM function-call control loop.

n8n has separate real-container execution verification. External OpenAI execution remains a separate credential-gated verification step.

See `TESTING.md` for exact scope and limitations.

## Honest limitations

This project does **not** demonstrate:

- years of production AI-engineering experience;
- training or fine-tuning a foundation model;
- real customer-system access;
- production Salesforce/Jira/Zendesk/Slack writes;
- enterprise identity/RBAC or tenant isolation;
- production-grade vector retrieval with ACL filtering;
- comprehensive prompt-injection defense;
- load testing or SRE-level production operation;
- a verified real external OpenAI call until the private credential-backed verification passes;
- Avalara production AI work.

The correct description is a personal applied-AI portfolio built from real Technical Support/API troubleshooting domain experience.

# Likely interview questions

## 1. What problem were you trying to solve?

**Technical answer:** I wanted to model the evidence-gathering and escalation workflow of enterprise support: retrieve bounded context, classify the issue, recommend troubleshooting, and route high-risk cases to a human.

**Plain-English:** I automated the repetitive investigation steps a support engineer normally performs before deciding what to try or when to escalate.

## 2. Why is this an agent?

**Technical answer:** In live mode the model can iteratively request allow-listed tools, observe results, and continue the investigation within a bounded control loop.

**Plain-English:** It can decide which approved clue it needs next instead of only answering one prompt.

## 3. Why did you keep an offline deterministic mode?

**Technical answer:** It gives a reproducible public demo, supports regression testing, reduces external dependencies, and clearly separates deterministic business logic from provider inference.

**Plain-English:** The demo still works reliably even if an AI API or internet connection is unavailable.

## 4. Where do LLMs add value here?

**Technical answer:** Natural-language interpretation, tool selection, and evidence synthesis are good probabilistic tasks; high-risk policy and permissions remain deterministic.

**Plain-English:** AI is useful for understanding messy support language, but I do not let it control safety rules.

## 5. Why not let the model do everything?

**Technical answer:** LLM behavior is probabilistic. Severity policy, permissions, execution limits, and consequential actions need deterministic enforcement and human control.

**Plain-English:** An AI can be wrong, so important rules should not depend on its opinion alone.

## 6. What is tool calling?

**Technical answer:** The model emits a structured function-call request that matches a strict schema; Python validates and executes the allow-listed function, then returns the observation to the model.

**Plain-English:** The AI can ask the program to use an approved tool, but the program—not the AI—actually runs it.

## 7. What tools can the agent use?

**Technical answer:** Synthetic knowledge search, customer lookup, service-status lookup, bounded log query, and an escalation-preview tool.

**Plain-English:** It can look up documentation, customer context, status, logs, and create a safe escalation preview.

## 8. What is RAG in this project?

**Technical answer:** The local knowledge search retrieves only relevant synthetic knowledge snippets and adds those observations to the investigation rather than sending the entire knowledge base.

**Plain-English:** It finds the few pieces of documentation relevant to the problem instead of giving the AI everything.

## 9. How do you control tokens/context?

**Technical answer:** I bound ticket characters, approximate input-token budget, evidence count, live context items, tool rounds, and maximum model output tokens.

**Plain-English:** I limit how much information the AI can consume and how long the workflow can continue.

## 10. Is the offline token number exact?

**Technical answer:** No. It is deliberately labeled as a rough local estimate. Provider-reported token usage is kept separate in live mode.

**Plain-English:** No—the offline number is an estimate, and the UI says so.

## 11. How do you estimate cost?

**Technical answer:** I do not hard-code pricing. If current per-million-token rates are supplied through environment variables, the runtime can calculate an approximate cost from provider-reported token counts.

**Plain-English:** Prices change, so I only calculate cost when current rates are explicitly configured.

## 12. What happens if a tool fails?

**Technical answer:** The synthetic failure path records the tool error, triggers a deterministic guardrail, and forces human review instead of pretending the evidence is complete.

**Plain-English:** It stops being confident and sends the case to a person.

## 13. What is human-in-the-loop?

**Technical answer:** A high-risk route pauses at a decision boundary where a human can approve, reject, or escalate. The demo records the choice but still performs no external write.

**Plain-English:** A person gets the final say before anything important could happen.

## 14. Did you connect this to Jira or Slack?

**Technical answer:** No. External actions are deliberately preview-only in the public portfolio.

**Plain-English:** No. I demonstrate the safe decision point without touching real systems.

## 15. How is n8n used?

**Technical answer:** n8n demonstrates event/workflow orchestration around normalization, classification, deterministic guardrails, and human routing. CI verifies real import and execution in the official n8n container.

**Plain-English:** n8n is the workflow coordinator that moves an incident through the steps.

## 16. Did you actually run n8n?

**Technical answer:** Yes. The GitHub Actions workflow launches the official container, imports the workflow, executes it, and requires a PASS result.

**Plain-English:** Yes—the workflow is executed automatically in CI, not just stored as a diagram.

## 17. Did you actually run the live OpenAI path?

**Technical answer:** The function-call control loop is automated with a deterministic mock provider. Real external execution is a separate credential-gated verification and should only be claimed after that run succeeds.

**Plain-English:** The integration code is tested, but I keep a real paid API call as a separate verification so I do not exaggerate what was run.

## 18. Why FastAPI?

**Technical answer:** It exposes the workflow through validated REST endpoints and generated OpenAPI docs, making the project easy to test with Postman or another client.

**Plain-English:** It turns the Python logic into an API that other applications can call.

## 19. How would you productionize it?

**Technical answer:** Add SSO/RBAC, tenant isolation, durable audit/tracing, secrets management, PII redaction, production connectors, ACL-aware retrieval, stronger injection defenses, rate limiting, model fallbacks, formal eval datasets, and service-level monitoring.

**Plain-English:** I would add enterprise security, real integrations, stronger monitoring, and much more rigorous testing before using it with real customers.

## 20. What did you personally learn from building this?

**Technical answer:** I learned how support-domain logic maps into an agent architecture: tool schemas, control loops, deterministic guardrails, context/token budgeting, observability, workflow orchestration, and honest verification boundaries.

**Plain-English:** I learned how to turn support troubleshooting experience into a controlled AI workflow instead of just prompting ChatGPT.

## Best demo sequence

1. Run **401 credential rotation**.
2. Open **AI Usage & Observability** and point out tools, evidence limits, token labeling, decision trace, and zero external action.
3. Run **Synthetic diagnostic-tool failure** and show that the workflow routes to human review.
4. Open **Incident Router**, choose the P1 outage, then click one of the human-decision buttons.
5. Show `NIGEL_AI_SKILLS_MATRIX.md` or `ARCHITECTURE.md` if the interviewer wants code/architecture detail.

## Five files to study first

1. `INTERVIEW_GUIDE.md`
2. `NIGEL_AI_SKILLS_MATRIX.md`
3. `ARCHITECTURE.md`
4. `atlas_support_agent/agent.py`
5. `atlas_support_agent/live_agent.py`

## What not to claim

Do **not** say:

- this was built at Avalara or another former employer;
- the synthetic tools connect to real customer systems;
- n8n is a former employer's internal automation standard;
- a mocked provider test is the same thing as a real external LLM call;
- live OpenAI execution was validated until the credential-gated verification has actually passed;
- the project is production-ready;
- you are a senior ML engineer or have years of production AI engineering experience.

Accurate wording:

> This is a personal portfolio project built from my support and API troubleshooting experience. I intentionally used synthetic data so I could publish and demonstrate the architecture safely.
