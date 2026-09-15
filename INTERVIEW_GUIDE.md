# Interview Guide — Agentic AI Support Portfolio

This guide keeps the portfolio explanation accurate, concise, and defensible.

## 30-second explanation

> I modernized my Technical Support and API troubleshooting background by building a Python-based agentic support portfolio. The flagship workflow retrieves synthetic support evidence through controlled tools, classifies incidents, exposes REST endpoints through FastAPI, and applies deterministic escalation guardrails. I also built and actually executed an n8n orchestration workflow in CI, plus a credential-gated OpenAI Responses API path with function calling and token/latency telemetry. All public data is synthetic so the architecture is safe to demonstrate.

## Five-minute walkthrough

1. **Start with the problem** — support teams spend time gathering evidence across documentation, customer context, service status, and logs.
2. **Show Atlas Support AI Agent** — a ticket becomes an evidence-backed investigation using allow-listed support tools.
3. **Explain RAG-style retrieval** — the agent retrieves only relevant synthetic knowledge instead of dumping all documentation into context.
4. **Explain guardrails** — P1 and high-risk signals are evaluated deterministically; consequential actions are preview-only.
5. **Show FastAPI/Postman** — the same logic is exposed through REST endpoints with OpenAPI documentation and regression-tested endpoint behavior.
6. **Show n8n** — explain the executable workflow: trigger → normalization → classification → deterministic guardrail → human-routing decision. The repository's GitHub Actions job imports and executes this workflow inside the official n8n container.
7. **Show evaluations and observability** — regression tests verify core classification, escalation, API diagnostics, endpoints, and the LLM control loop/telemetry plumbing.
8. **Explain the live-provider boundary accurately** — the real OpenAI path is implemented and has a fail-closed verification script, but it is only called externally verified after a private API credential is configured and that manual verification run passes.

## Key concepts

### Agent vs. chatbot
A chatbot mainly responds to a prompt. An agent can decide it needs evidence, request an allow-listed tool, receive the tool result, continue its investigation, and then produce a final response.

### Tool/function calling
The optional live agent defines a small set of functions with JSON schemas. The model can request one of those functions, but the application—not the model—executes it. This keeps system access narrow and auditable.

The control loop is covered by an automated test using a deterministic mock provider. That proves the application's function-call plumbing and telemetry handling. It does **not** by itself prove a real provider network call.

### RAG
Retrieval-Augmented Generation retrieves relevant knowledge before or during reasoning so the answer is grounded in source material. The public offline demo uses a transparent local retrieval pattern over synthetic knowledge.

### Token/context controls
The portfolio bounds ticket size, evidence volume, tool rounds, and model output. Live mode records token usage and latency when the API provides it. The purpose is to manage cost, latency, context quality, and runaway workflows.

### Guardrails
The LLM is probabilistic, so high-risk incident signals also pass through deterministic Python policy. A P1/high-risk event cannot rely only on model judgment.

### Human in the loop
The workflow creates an escalation preview. It does not send a real message, create a Jira ticket, or modify production data without a human-controlled integration.

### n8n
n8n is used as an orchestration layer. This is now more than an importable diagram: GitHub Actions launches the official n8n container, imports the repository workflow, resolves its workflow ID, executes it, and requires a `verification: PASS` result.

For the verified synthetic ticket, the n8n workflow produced:

```text
severity: P2
category: authentication
reason: Authentication failure after credential rotation
escalate: false
human_approval_required: false
```

### FastAPI and Postman
FastAPI exposes the Python workflow as REST endpoints with generated OpenAPI documentation. Postman can call those endpoints exactly as a client application would. Endpoint behavior is also covered with FastAPI TestClient regression tests.

### Evals / observability
The automated suite verifies deterministic behavior and the internal LLM tool-call loop. The live path returns model name, tools used, token usage, output limits, and latency.

## What is verified today

| Capability | Accurate interview wording |
|---|---|
| Python support automation | "I built and regression-tested the Python support workflows." |
| FastAPI | "I exposed the workflows through FastAPI and tested the endpoints." |
| Guardrails | "I added deterministic escalation policy and human-approval boundaries." |
| n8n | "I built an n8n workflow and verified a real import and execution in the official n8n container through GitHub Actions." |
| Function-call loop | "I implemented and automated tests for the LLM function-call control loop and telemetry plumbing." |
| External OpenAI execution | Until a credential-backed verification passes: "The real OpenAI path is implemented and ready for credential-backed verification; I keep that separate from the mocked control-loop test." |

## Best demo scenario

Use this first:

```text
Customer CUST-101 is receiving HTTP 401 errors after rotating production credentials. Postman works, but the production integration still fails.
```

Why it works well:
- familiar API/support problem;
- demonstrates Postman and credential-rotation reasoning;
- uses customer context, logs, and knowledge retrieval;
- shows a structured resolution without immediately jumping to P1.

Then show the P1 guardrail:

```text
Production down - complete outage for all customers.
```

The deterministic policy should require escalation and create only a preview.

## If Nigel asks, "Did you actually run n8n?"

> Yes. I initially had an importable workflow artifact, but I didn't want to claim n8n experience from a JSON file alone. I added a GitHub Actions verification that runs the official n8n container, imports the workflow, executes it, and fails unless the workflow produces the expected PASS result. I had to troubleshoot container permissions and current n8n workflow metadata before the final execution passed.

That answer is especially useful because it shows both orchestration work and real integration debugging.

## If asked about the live LLM

Before a real credential-backed run succeeds, use this wording:

> I implemented the OpenAI Responses API path with allow-listed function calling, bounded tool rounds, token limits, and token/latency telemetry. I also built a deterministic automated test around the control loop. I keep real provider verification separate because I don't want to represent a mocked API client as a live external model run.

After `scripts/verify_live_llm.py` succeeds with a private API credential, you can truthfully change that to:

> I also executed the workflow against the live OpenAI Responses API and verified that the model called an allow-listed support tool while I captured token usage and end-to-end latency.

## What not to claim

Do **not** say:
- this was built at Avalara or another former employer;
- the synthetic tools connect to real customer systems;
- n8n is a former employer's internal automation standard;
- a mocked provider test is the same thing as a real external LLM call;
- live OpenAI execution was validated until the credential-gated verification has actually passed;
- the project is production-ready.

Accurate wording:

> This is a personal portfolio project built from my support and API troubleshooting experience. I intentionally used synthetic data so I could publish and demonstrate the architecture safely.

## Productionization discussion

If asked what would come next:
- SSO/RBAC and tenant isolation
- secret/PII redaction
- production-grade Salesforce/Jira/Zendesk connectors
- Datadog/Splunk/Elastic log integrations
- vector retrieval with ACL filtering
- prompt-injection defenses for retrieved content
- audit logging and trace persistence
- formal offline/online evaluation datasets
- model routing, fallbacks, and circuit breakers
- cost/latency dashboards
- deployment, CI/CD, and service-level monitoring
