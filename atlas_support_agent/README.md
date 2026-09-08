# Atlas Support AI Agent

The flagship project in the portfolio: an evidence-backed Technical Support investigation workflow built around controlled agent design.

## What it does

Given a synthetic support ticket, Atlas can:

1. identify a customer ID;
2. retrieve relevant synthetic knowledge;
3. inspect synthetic customer metadata;
4. check synthetic service status;
5. query bounded synthetic logs;
6. classify severity and category;
7. produce troubleshooting steps and customer/internal notes;
8. apply deterministic P1/high-risk escalation policy;
9. create a preview-only escalation record when required.

## Two execution paths

### Offline deterministic path — verified

`agent.py` is fully runnable with no external API. It exercises the same support concepts in a reproducible way and is covered by regression tests.

### Optional live tool-calling path

`live_agent.py` uses the OpenAI Responses API. The model receives only a small set of allow-listed function schemas:

- `search_knowledge_base`
- `lookup_customer`
- `check_service_status`
- `query_logs`
- `create_escalation_preview`

The application executes requested functions and returns the results to the model. The model never receives unrestricted access to a production system.

## Guardrail model

```text
LLM recommendation
        +
Deterministic Python policy
        +
Human approval for consequential action
        =
Controlled support workflow
```

P1/high-risk conditions such as complete outage, production down, data loss, or security breach cannot rely only on probabilistic model judgment.

## Context and token controls

The public implementation bounds:

- ticket input length;
- evidence count;
- log results;
- LLM tool rounds;
- LLM output tokens.

Live mode also returns token-usage and latency telemetry when the API provides it.

## Best demo ticket

```text
Customer CUST-101 is receiving HTTP 401 errors after rotating production credentials. Postman works, but the production integration still fails.
```

This demonstrates API troubleshooting, customer context, logs, retrieval, and a clean resolution path without immediately escalating to P1.

## Safety

All data is synthetic. `create_escalation_preview` is intentionally preview-only and never changes an external system.