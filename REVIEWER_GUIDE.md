# 60-Second Reviewer Guide

This portfolio is designed to be easy to evaluate quickly.

## Start here

**Live demo:** https://ai-support-portfolio-production.up.railway.app

Use the default sample ticket in **Customer Issue Investigation** and click **Analyze Customer Issue**.

You will see a plain-English investigation of a synthetic HTTP 401 credential-rotation issue, including severity, reproduction status, technical evidence, missing information, troubleshooting steps, a customer-facing update, and an engineering-ready handoff.

## What this demonstrates

- **Python** support investigation and automation logic
- **Engineering handoff generation** with expected/actual behavior, reproduction, evidence, confidence, and next engineering checks
- **Generic SAML SSO / SCIM diagnostics** using synthetic evidence only
- **Explainable duplicate/pattern detection** and synthetic Support Operations metrics
- **Missing-information detection** so vague tickets request evidence instead of inventing it
- **FastAPI** REST service with structured request/response validation
- **Postman-ready** API endpoints
- **Controlled agent architecture** with allow-listed tools
- **RAG-style retrieval** over synthetic support knowledge
- **Deterministic guardrails** for P1/high-risk conditions
- **Human-in-the-loop** escalation boundaries
- **Token/context/tool-round controls**
- **Token and latency telemetry plumbing**
- **n8n workflow orchestration**, imported and executed successfully in the official n8n container through GitHub Actions
- **Automated regression tests and CI**

## Recommended 3-minute review

1. Open the **live demo** and run the default **Customer Issue Investigation** scenario.
2. Generate the **Customer Update** and explain the customer-facing communication boundary.
3. Generate the **Engineering Handoff** and show reproduction, evidence, confidence, and recommended engineering investigation.
4. Open **Support Operations** to show deterministic duplicate detection and synthetic support metrics.
5. Run the **Synthetic diagnostic-tool failure** scenario and show that incomplete evidence routes to human review.
6. Open **Architecture & Automation** to show the n8n workflow and deterministic-vs-probabilistic control boundaries.
7. Review `VERIFICATION.md` for evidence of what has actually run.
8. Review `atlas_support_agent/live_agent.py` for the bounded Responses API function-calling loop.
9. Review `.github/workflows/n8n-verification.yml` and `n8n_runner/workflow.json` for the executed n8n workflow.

## Verification boundary

The portfolio intentionally distinguishes between code that exists and code that has been executed.

**Verified:** Python support logic, FastAPI endpoint behavior, deterministic guardrails, function-call control-loop plumbing, telemetry plumbing, and real n8n import/execution.

**Credential-gated:** the external OpenAI Responses API path is implemented with a fail-closed verifier but is not labeled as externally verified until a private API credential is used successfully.

## Safety and confidentiality

All customers, tickets, logs, status records, SAML/SCIM examples, request IDs, browser/network evidence, SLA values, dashboard metrics, and product examples are synthetic. No Avalara or former-employer customer information, credentials, internal documentation, or proprietary data is included. The identity scenario is generic enterprise troubleshooting and does not represent TheyDo's internal implementation.

## One-sentence summary

> I modernized the Technical Support and API troubleshooting work I already know by building a Python-based support-operations portfolio with controlled agent tooling, REST APIs, evidence-based engineering handoffs, deterministic guardrails, n8n orchestration, automated testing, and human approval boundaries.
