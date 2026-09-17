# Nigel AI Skills Matrix

This matrix maps the portfolio to the practical AI-building areas Nigel highlighted. It is intentionally conservative: a capability is marked **YES** only when the repository contains a concrete implementation or verified workflow.

| Skill | Demonstrated? | Where | How I can explain it |
|---|---|---|---|
| AI agents | YES | `atlas_support_agent/agent.py`, `atlas_support_agent/live_agent.py` | The support workflow gathers evidence, routes through approved tools, evaluates observations, applies policy, and returns a recommendation or human escalation path rather than acting like a free-form chatbot. |
| LLM integration | PARTIAL | `atlas_support_agent/live_agent.py`, `scripts/verify_live_llm.py` | I implemented the OpenAI Responses API path with function calling and telemetry. The internal control loop is regression-tested; a real external provider run is kept as a separate credential-gated verification boundary. |
| Python scripting | YES | Core repository Python modules | Python handles routing, API logic, guardrails, evidence handling, telemetry, tests, and workflow helpers. |
| API integration | YES | `api.py`, live LLM client, API diagnostics | FastAPI exposes validated REST endpoints, while the optional live path calls a model API through a controlled client. |
| n8n | YES | `incident_escalation_automation/01_support_escalation_router.n8n.json`, `n8n_runner/`, `.github/workflows/n8n-verification.yml` | I built an importable workflow and added CI that launches the official n8n container, imports it, executes it, and checks the result. |
| Token controls | YES | `atlas_support_agent/runtime.py`, `live_agent.py` | The project bounds output tokens and approximates a preflight input budget. Live mode captures provider-reported input/output usage where available. |
| Context management | YES | `runtime.py`, `_bound_context()` in `live_agent.py`, bounded evidence in `agent.py` | The application caps ticket size, evidence items, context items, and tool rounds instead of sending unlimited history. |
| Structured outputs | YES | Pydantic `Investigation` model, FastAPI models | Core results use explicit schemas so downstream code does not depend on parsing free-form prose. |
| Tool calling | YES | `TOOLS` and `_run_tool()` in `live_agent.py` | The model can request only defined synthetic tools with strict JSON schemas; Python executes the tool. |
| Deterministic logic | YES | `_classify()`, incident router, API diagnostics | High-risk and support-routing decisions have deterministic Python paths separate from the LLM. |
| Guardrails | YES | high-risk checks, tool allow-list, limits, preview-only actions | P1/high-risk signals and synthetic tool failures route toward human review; external writes are disabled. |
| Human-in-the-loop | YES | `apply_human_decision()`, Streamlit incident UI | High-risk incidents expose approve/reject/escalate choices, but the demo still records zero external actions. |
| Observability | YES | offline telemetry, live telemetry, decision trace, tool events | Runs expose request IDs, tools, timing, limits, context counts, guardrails, and provider token telemetry in live mode. |
| Error handling | YES | API validation, safe live errors, synthetic tool-failure scenario | Invalid HTTP inputs are rejected, live failures are bounded, and a diagnostic-tool failure explicitly forces human review. |
| Testing | YES | `test_portfolio.py`, agent tests, GitHub Actions | Regression tests cover routing, API behavior, guardrails, telemetry, the mock-provider function-call loop, and human approval boundaries. |
| Deployment | YES — portfolio/demo | Railway `ai-support-portfolio` + `Procfile` | The Streamlit portfolio is designed for a public demo deployment. This should not be described as enterprise production readiness. |
| Security | YES — portfolio controls | `.gitignore`, `.env.example`, synthetic data, allow-list, preview-only actions | Credentials are environment-based, public data is synthetic, and external writes are not enabled. Production security controls would still be needed for a real system. |

## Most important accuracy boundary

The strongest accurate description is:

> I am a Technical Support / TAM professional who has begun building practical agentic-AI systems around workflows I already understand deeply: API troubleshooting, evidence gathering, incident severity, escalation, customer communication, and support automation.

Do not describe the project as former-employer production work, do not claim years of AI-engineering experience, and do not claim a real external LLM call has been verified until the credential-gated verification has actually passed.
