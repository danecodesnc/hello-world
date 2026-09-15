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

The control-loop implementation is covered by `test_live_agent_loop.py`, which uses a deterministic mock provider to verify function-call handling, tool execution, final-response handling, token counters, tool tracking, and latency plumbing. That test verifies the application logic, but it is intentionally not presented as proof of a real external provider call.

## Real-provider verification

A separate fail-closed verifier is provided at:

```text
scripts/verify_live_llm.py
```

With a private `OPENAI_API_KEY` configured, run:

```bash
python scripts/verify_live_llm.py
```

The verifier only passes if it observes:

- `mode == live_llm`;
- a provider model identifier;
- non-empty final model output;
- at least one allow-listed function call;
- input-token telemetry;
- output-token telemetry;
- positive end-to-end latency.

The repository also includes a manually triggered GitHub Actions workflow at `.github/workflows/live-llm-verification.yml`. It requires a private GitHub Actions secret named `OPENAI_API_KEY` and fails if the credential is absent.

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

Live mode returns token-usage and latency telemetry when the API provides it.

## Best demo ticket

```text
Customer CUST-101 is receiving HTTP 401 errors after rotating production credentials. Postman works, but the production integration still fails.
```

This demonstrates API troubleshooting, customer context, logs, retrieval, and a clean resolution path without immediately escalating to P1.

## Safety

All data is synthetic. `create_escalation_preview` is intentionally preview-only and never changes an external system.
