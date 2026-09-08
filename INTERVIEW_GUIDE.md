# Interview Guide — Agentic AI Support Portfolio

This guide keeps the portfolio explanation accurate, concise, and defensible.

## 30-second explanation

> I modernized my Technical Support and API troubleshooting background by building a Python-based agentic support portfolio. The flagship workflow can retrieve synthetic support evidence, call approved tools, classify incidents, expose REST endpoints through FastAPI, apply deterministic escalation guardrails, and optionally use an LLM through controlled function calling. I also built an n8n escalation workflow and an API diagnostics utility. All public data is synthetic so the architecture is safe to demonstrate.

## Five-minute walkthrough

1. **Start with the problem** — support teams spend time gathering evidence across documentation, customer context, service status, and logs.
2. **Show Atlas Support AI Agent** — a ticket becomes an evidence-backed investigation using allow-listed support tools.
3. **Explain RAG-style retrieval** — the agent retrieves only relevant synthetic knowledge instead of dumping all documentation into context.
4. **Explain guardrails** — P1 and high-risk signals are evaluated deterministically; consequential actions are preview-only.
5. **Show FastAPI/Postman** — the same logic is exposed through REST endpoints with OpenAPI documentation.
6. **Show n8n** — a visual workflow can normalize an event and route it based on severity, with human approval for the high-risk branch.
7. **Show evaluations** — regression tests verify core classification, escalation, API diagnostics, and endpoint behavior.

## Key concepts

### Agent vs. chatbot
A chatbot mainly responds to a prompt. An agent can decide it needs evidence, request an allow-listed tool, receive the tool result, continue its investigation, and then produce a final response.

### Tool/function calling
The optional live agent defines a small set of functions with JSON schemas. The model can request one of those functions, but the application—not the model—executes it. This keeps system access narrow and auditable.

### RAG
Retrieval-Augmented Generation retrieves relevant knowledge before or during reasoning so the answer is grounded in source material. The public offline demo uses a transparent local retrieval pattern over synthetic knowledge.

### Token/context controls
The portfolio bounds ticket size, evidence volume, tool rounds, and model output. Live mode also records token usage and latency. The purpose is to manage cost, latency, context quality, and runaway workflows.

### Guardrails
The LLM is probabilistic, so high-risk incident signals also pass through deterministic Python policy. A P1/high-risk event cannot rely only on model judgment.

### Human in the loop
The workflow creates an escalation preview. It does not send a real message, create a Jira ticket, or modify production data without a human-controlled integration.

### n8n
n8n is used as an orchestration layer. The public artifact demonstrates ticket intake, normalization, classification/routing, and a human-approval boundary for high-risk events.

### FastAPI and Postman
FastAPI exposes the Python workflow as REST endpoints with generated OpenAPI documentation. Postman can call those endpoints exactly as a client application would.

### Evals / observability
Tests verify deterministic behavior. Optional live mode exposes telemetry for model name, tools used, token usage, output limits, and latency.

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

## What not to claim

Do **not** say:
- this was built at Avalara or another former employer;
- the synthetic tools connect to real customer systems;
- n8n is a former employer's internal automation standard;
- live LLM mode was validated if you have not personally executed it with your own API credential;
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
