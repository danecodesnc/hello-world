# Testing Guide

The portfolio uses deterministic regression tests for the public-safe path and separate verification for integration boundaries.

## Run the local regression suite

```bash
pytest -q
```

The GitHub Actions workflow `.github/workflows/tests.yml` installs `requirements.txt` on Python 3.12 and runs the same command on pushes and pull requests.

## What the regression suite covers

### Support-agent behavior

- 401 / credential-rotation classification
- P1 complete-outage guardrail
- synthetic diagnostic-tool failure routing to human review
- bounded observability metadata
- rough offline token-estimate labeling
- tool usage and structured output

### Interview-focused support operations behavior\n\n- SAML SSO / SCIM classification and generic identity diagnostics\n- reproduction-status calculation\n- missing-information detection\n- engineering-ready handoff generation\n- customer-facing update generation\n- explainable duplicate grouping\n- synthetic support-operations metrics\n- REST endpoints for handoff, customer updates, duplicates, and metrics\n### Human-in-the-loop behavior

- P1 incidents require human approval
- approve/reject/escalate decisions produce a record
- the decision record never claims an external action occurred

### REST API behavior

- health endpoint
- offline investigation endpoint
- synthetic tool-failure endpoint path
- request validation for too-short input
- human-decision endpoint
- API-diagnostics endpoint

### API diagnostics

- authentication errors
- service/unavailable errors
- escalation rules

### LLM control-loop test

`atlas_support_agent/test_live_agent_loop.py` replaces the external provider client with a deterministic fake client. This test verifies:

- the function-call loop;
- allow-listed tool execution;
- tool-event telemetry;
- input/output/total token accounting plumbing;
- runtime limits;
- zero external action.

This test proves the application's integration logic. It does **not** prove a real external model network call.

## n8n verification

`.github/workflows/n8n-verification.yml` uses the official n8n container to import and execute the repository workflow and checks the expected verification result. This is separate from the Python regression suite because it verifies a different runtime.

## Live provider verification

`scripts/verify_live_llm.py` is credential-gated and should fail closed when a private provider credential is missing or when the expected live evidence is not observed.

A real-provider verification is only considered complete when the run records:

- live mode;
- provider model identifier;
- non-empty model output;
- at least one allow-listed function call;
- positive provider-reported input tokens;
- positive provider-reported output tokens;
- measured latency.

## Failure scenarios deliberately exercised

The repository contains or validates paths for:

- missing API key;
- invalid/too-short REST input;
- bounded live-provider failure output;
- malformed tool arguments in the live loop;
- synthetic diagnostic-tool failure;
- low-confidence/ambiguous evidence;
- high-risk/P1 escalation;
- context and execution limits.

## Mocked vs. real systems

| Component | Test mode |
|---|---|
| Synthetic customer/status/log/KB tools | Local deterministic data |
| FastAPI | Real application code via TestClient |
| LLM control loop | Mock provider client in automated tests |
| n8n | Real n8n container execution in CI |
| External OpenAI provider | Separate credential-gated verification only |
| Jira / Slack / CRM / customer systems | Not connected; preview-only by design |

## Known testing limitations

This is a portfolio/demo project, not a production certification suite. It does not currently include load testing, adversarial red-team coverage, multi-tenant authorization testing, persistent audit-store testing, browser E2E automation, or production connector contract tests.
