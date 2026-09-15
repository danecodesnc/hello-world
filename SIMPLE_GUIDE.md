# Simple Guide — Dane's AI Support Portfolio

## The easiest way to use it

Open the live demo:

**https://ai-support-portfolio-production.up.railway.app**

Nothing needs to be installed. Open the link, choose a tab, and click a button.

## What the portfolio does

### 🔎 Support Helper
Reads a sample customer problem, gathers clues, identifies the likely issue, recommends what to try next, and decides whether a human should step in.

### 🚨 Incident Router
Looks at an incident and decides how urgently it should be handled. High-risk situations are routed for human review instead of allowing the system to take consequential action on its own.

### 🌐 API Error Helper
Explains common API errors such as 401, 403, 429, 500, 503, and 504 and provides a simple troubleshooting checklist.

### 🔁 n8n Workflow
Shows how a support ticket can move through an automation pipeline: receive the ticket, classify it, apply a safety rule, and decide whether a human needs to review it.

This is not just a picture of a workflow. The repository automatically launches a real n8n container, imports the workflow, runs it, and checks that it finishes successfully.

## Easy demo

1. Open the live portfolio.
2. Choose **Support Helper**.
3. Leave the sample ticket exactly as it is.
4. Click **Analyze Support Ticket**.
5. Read the plain-English result.
6. Try **API Error Helper** with **401** selected.

## What has actually been tested

- Python support logic: **tested**
- FastAPI endpoints: **tested**
- Escalation safety rules: **tested**
- n8n workflow import and execution: **tested in a real n8n container**
- LLM tool-calling program logic and telemetry: **tested with a controlled mock provider**
- Real external OpenAI call: **ready for a private API key, but not labeled verified until that real run succeeds**

## Why I built it

I wanted to combine the Technical Support and API troubleshooting work I already know with newer AI and automation skills, including Python, FastAPI, controlled agent workflows, guardrails, n8n orchestration, testing, and observability.

## Confidentiality

All customers, tickets, logs, service data, and product examples are fictional. This public portfolio contains no Avalara customer data, credentials, internal documentation, or other proprietary information.

## One-sentence explanation

> I built and tested a support-automation portfolio that combines my existing API and Technical Support experience with Python, controlled AI-agent workflows, FastAPI, n8n orchestration, safety guardrails, and automated verification.
