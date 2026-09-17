# Incident & Escalation Automation

A support-operations workflow demonstrating severity-based routing, deterministic guardrails, n8n orchestration, and human-in-the-loop controls.

## Python routing logic

`router.py` classifies synthetic incident text into:

- **P1** → human escalation preview; approval required
- **P2** → senior support review
- **P3** → standard support route

The logic is deliberately deterministic so high-risk routing does not depend solely on an LLM.

The module also exposes `apply_human_decision()` so the public demo can record **Approve**, **Reject**, or **Escalate** decisions without taking any external action.

## n8n workflow artifact

`01_support_escalation_router.n8n.json` is an importable workflow using only synthetic data and no credentials.

### Node-by-node flow

```text
Manual Trigger
      ↓
Synthetic Ticket / Event
      ↓
Normalize input
      ↓
Classify + deterministic guardrail
      ↓
Severity / route / human-approval decision
      ↓
Verification output
```

The separate `n8n_runner/workflow.json` and `.github/workflows/n8n-verification.yml` provide executable verification for the orchestration pattern.

## Human-in-the-loop design

High-risk conditions such as complete outage, production down, security breach, or data loss produce a preview-only route that requires a human decision before a consequential integration would be allowed to act.

The Streamlit demo now exposes the approval boundary interactively. Even after a user clicks approve/reject/escalate, the result explicitly states `external_action_taken: false`.

## Public-demo safety

This workflow does **not** send Slack messages, create Jira tickets, modify customer systems, or write production data.

## How n8n is verified

The repository's **n8n Workflow Verification** GitHub Actions job launches the official n8n container, imports the verification workflow, executes it, and fails unless the workflow produces the expected PASS result.

That means the accurate interview statement is:

> I built an n8n orchestration workflow and verified real import and execution in the official n8n container through GitHub Actions.

It should **not** be described as a production integration with Jira, Slack, Salesforce, Zendesk, or a former employer.

## Importing manually

In an n8n environment, use the workflow import feature and select `01_support_escalation_router.n8n.json`. The workflow contains no secrets. Review every node before attaching any real credential or external action in a private environment.
