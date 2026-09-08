# Incident & Escalation Automation

A support-operations workflow demonstrating severity-based routing and human-in-the-loop controls.

## Python routing logic

`router.py` classifies synthetic incident text into:

- **P1** → human escalation preview; approval required
- **P2** → senior support review
- **P3** → standard support route

The logic is deliberately deterministic so high-risk routing does not depend solely on an LLM.

## n8n workflow artifact

`01_support_escalation_router.n8n.json` is an importable workflow design containing:

```text
Manual Trigger
      ↓
Synthetic Ticket
      ↓
Classify + Guardrail
      ↓
Severity / Route / Human Approval Decision
```

The workflow uses only synthetic data and does not contain credentials.

## Human-in-the-loop design

High-risk conditions such as complete outage, production down, security breach, or data loss produce a preview-only route that requires human approval before a consequential integration would be allowed to act.

## Public-demo safety

This workflow does **not** send Slack messages, create Jira tickets, modify customer systems, or write production data.

## Verification note

The Python routing path is covered by the repository regression suite. The n8n JSON is published as an importable portfolio artifact; it should be described as workflow design until it has been personally imported and executed in an n8n environment.