# Security & Safety Boundaries

This repository is a public portfolio project. Its security design focuses on demonstrating safe architecture patterns without pretending to provide enterprise production controls.

## Public-data policy

All customer IDs, tickets, logs, knowledge-base text, service-status records, product names, and incident scenarios are fictional/synthetic.

Do not add:

- real customer data;
- employer-internal documentation;
- production logs;
- access tokens;
- API keys;
- passwords;
- private endpoints;
- proprietary incident details.

## Secret handling

- `OPENAI_API_KEY` is read from the environment.
- `.env` is ignored by Git and must never be committed.
- `.env.example` contains only placeholders and configuration defaults.
- logs and UI output should never print a credential.
- provider pricing is not hard-coded; optional cost-estimation rates are environment configuration.

If a real secret is ever accidentally committed, remove it from active configuration and rotate/revoke the credential. Removing a string from the latest file alone is not sufficient to make a leaked credential safe.

## Tool-access boundary

The optional live agent has an explicit allow-list of synthetic support tools. The model cannot choose an arbitrary Python function, shell command, filesystem operation, or external connector.

Tool arguments use JSON schemas with `additionalProperties: false`, and tool execution failures are converted into bounded error records.

## External-write boundary

This portfolio intentionally does not create or modify records in Jira, Slack, Salesforce, Zendesk, a customer environment, or a production database.

Escalation is preview-only. The interactive human-in-the-loop demonstration records approve/reject/escalate decisions but always reports:

```text
external_action_taken: false
```

## Input/context controls

The repository bounds:

- ticket size;
- approximate preflight token budget;
- evidence items;
- live context items;
- live tool rounds;
- model output tokens.

These controls reduce runaway context growth, accidental cost expansion, and unbounded agent loops.

## Prompt-injection posture

The live system instruction explicitly treats user and retrieved content as untrusted evidence rather than as privileged instructions. The agent is constrained to allow-listed tools and has no enabled external-write capability.

This is a useful portfolio defense, but it is **not** a complete production prompt-injection security system. A real deployment would need stronger content isolation, ACL-aware retrieval, data-loss-prevention controls, security testing, and connector-specific authorization.

## Human review

High-risk/P1 conditions and diagnostic-tool failures route toward human review. Deterministic Python policy is used for these boundaries so a probabilistic model is not the sole authority for escalation.

## Production controls not implemented

A real enterprise version would still require:

- authentication and SSO;
- RBAC/ABAC;
- tenant isolation;
- durable audit logs;
- encryption/key-management review;
- secrets manager integration;
- PII/PCI/regulated-data redaction as applicable;
- production connector scopes and least privilege;
- rate limiting and abuse prevention;
- dependency and container scanning;
- incident-response procedures;
- retention/deletion policy;
- formal threat modeling and security review.

The correct positioning is **portfolio/demo safety controls**, not production security certification.
