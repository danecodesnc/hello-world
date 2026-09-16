# Verification Record

This file separates **implemented**, **automated-test verified**, and **real external execution verified** capabilities so the portfolio can be discussed accurately.

## Current status

| Capability | Evidence | Status |
|---|---|---|
| Python support investigation | Pytest regression suite | ✅ Verified |
| API diagnostics | Pytest regression suite | ✅ Verified |
| FastAPI endpoint behavior | FastAPI TestClient regression tests | ✅ Verified |
| P1/high-risk escalation guardrails | Regression tests | ✅ Verified |
| LLM function-call control loop | `atlas_support_agent/test_live_agent_loop.py` with deterministic mock provider | ✅ Application control loop verified |
| Token/tool/latency telemetry plumbing | `atlas_support_agent/test_live_agent_loop.py` | ✅ Instrumentation verified |
| n8n orchestration | `.github/workflows/n8n-verification.yml` using official `n8nio/n8n` container | ✅ Real n8n import + execution verified |
| External OpenAI Responses API | `scripts/verify_live_llm.py` + manual GitHub workflow | ⏳ Credential-gated; not marked verified until a real run passes |

## n8n execution evidence

Successful GitHub Actions run:

**https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/actions/runs/35034309127**

The verification job:

1. launched the official n8n container;
2. downloaded the repository workflow;
3. imported the workflow successfully;
4. exported/resolved the imported workflow ID;
5. executed the workflow with `n8n execute`;
6. required the execution log to contain `verification: PASS`.

The successful workflow output included:

```text
verification: PASS
orchestration: n8n trigger -> normalization -> classification -> deterministic guardrail -> human routing
severity: P2
category: authentication
reason: Authentication failure after credential rotation
escalate: false
human_approval_required: false
```

During verification, earlier runs exposed two real integration issues that were fixed before the final pass:

- the GitHub Actions container initially used a read-only n8n home/config location;
- current n8n import required workflow-level identity metadata.

A separate attempt to call the hosted FastAPI endpoint exposed a deployment architecture issue: the Railway public domain was routing to Streamlit rather than the FastAPI process. The final n8n verification was therefore made self-contained and deterministic rather than pretending the external HTTP call had succeeded.

## LLM control-loop evidence

`atlas_support_agent/test_live_agent_loop.py` verifies the application's orchestration around an LLM provider:

- provider returns a function call;
- application parses function arguments;
- only allow-listed synthetic tools are executed;
- tool output is returned into the control loop;
- a final model response is handled;
- tools used are recorded;
- input/output token counts are accumulated;
- latency is recorded;
- tool-round and output-token limits remain bounded.

This proves the **application-side agent loop and observability plumbing**. Because the provider is mocked in that automated test, it is not represented as a real external OpenAI call.

## Real OpenAI verification gate

A real credential-backed run uses:

```bash
python scripts/verify_live_llm.py
```

or the manually triggered GitHub Actions workflow:

```text
.github/workflows/live-llm-verification.yml
```

The verifier fails unless all of these are observed:

- live mode;
- provider model identifier;
- non-empty final output;
- at least one actual allow-listed function call;
- positive input-token count;
- positive output-token count;
- positive measured latency.

Until that run succeeds with a private `OPENAI_API_KEY`, the portfolio deliberately labels external OpenAI execution as **pending**, not verified.

## Deployment hygiene

The reviewer-facing Railway production environment was cleaned after verification so temporary n8n proof/debug services are not part of the final hosted portfolio. The live `ai-support-portfolio` service remains the production deployment used by reviewers.

## Interview rule

A repository artifact existing is not treated as evidence that it ran. Claims in this portfolio are intentionally limited to what can be supported by code, automated tests, or an execution record.
