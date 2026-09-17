from __future__ import annotations

import re
import time
import uuid

from pydantic import BaseModel, Field

from atlas_support_agent.runtime import (
    MAX_EVIDENCE_ITEMS,
    MAX_TICKET_CHARS,
    bound_text,
    rough_token_estimate,
)

HIGH_RISK_TERMS = {"production down", "complete outage", "security breach", "data loss", "data corruption", "credential leak"}

CUSTOMERS = {
    "CUST-101": {"plan": "Enterprise", "environment": "production", "integration": "REST API", "last_credential_rotation": "2026-09-01"},
    "CUST-202": {"plan": "Business", "environment": "production", "integration": "REST API"},
}
STATUS = {"state": "operational", "incidents": []}
LOGS = [
    {"customer_id": "CUST-101", "status": 401, "message": "invalid api key", "request_id": "req-demo-401-a"},
    {"customer_id": "CUST-101", "status": 401, "message": "authorization rejected", "request_id": "req-demo-401-b"},
    {"customer_id": "CUST-202", "status": 504, "message": "upstream timeout", "request_id": "req-demo-504-a"},
]
KB = [
    ("401 credential rotation", "If Postman works but production returns 401 after a rotation, compare the exact Authorization header and secret source used by the production runtime. Confirm the new credential propagated to the correct environment."),
    ("504 timeout", "Capture request IDs and timestamps, compare service health, and review bounded retry/backoff behavior."),
    ("429 rate limit", "Honor Retry-After, use exponential backoff with jitter, and reduce burst concurrency."),
    ("duplicate writes idempotency", "Before replaying a write, confirm whether the endpoint supports an idempotency key and whether a retry could duplicate data."),
]


class Investigation(BaseModel):
    severity: str = Field(pattern=r"^P[1-4]$")
    category: str
    confidence: float = Field(ge=0, le=1)
    likely_causes: list[str]
    troubleshooting_steps: list[str]
    escalate: bool
    human_approval_required: bool
    escalation_reason: str
    action_status: str
    customer_response: str
    internal_notes: str
    evidence: list[dict]
    tools_used: list[str]
    tool_errors: list[str]
    guardrails_triggered: list[str]
    decision_trace: list[dict]
    telemetry: dict


def _customer_id(ticket: str) -> str:
    m = re.search(r"CUST-\d+", ticket.upper())
    return m.group(0) if m else "CUST-101"


def _search_kb(ticket: str) -> list[dict]:
    words = {w.lower() for w in re.findall(r"[A-Za-z0-9]+", ticket) if len(w) > 2}
    scored = []
    for title, text in KB:
        score = len(words & {w.lower() for w in re.findall(r"[A-Za-z0-9]+", title + " " + text) if len(w) > 2})
        if score:
            scored.append((score, {"source": "synthetic_kb", "title": title, "detail": text}))
    return [item for _, item in sorted(scored, reverse=True, key=lambda x: x[0])[:2]]


def _classify(ticket: str, logs: list[dict]):
    t = ticket.lower()
    log_text = " ".join(str(x).lower() for x in logs)
    if "production down" in t or "complete outage" in t:
        return "P1", "availability", 0.97, ["Service availability incident"], ["Confirm blast radius", "Escalate to an incident owner", "Preserve request IDs and timestamps"]
    if "401" in t or "unauthorized" in t or "invalid api key" in log_text:
        return "P2", "authentication", 0.94, ["Stale or mismatched production credential", "Credential rotation did not propagate to the production runtime"], ["Compare the production Authorization header to the working Postman request", "Verify the secret source/environment", "Use request IDs to confirm the rejected credential path"]
    if "504" in t or "timeout" in t or "upstream timeout" in log_text:
        return "P2", "performance", 0.90, ["Upstream latency or timeout"], ["Capture request IDs and durations", "Check service health", "Review bounded retry/backoff behavior"]
    if "429" in t:
        return "P3", "rate_limit", 0.91, ["Rate limit exceeded"], ["Inspect Retry-After", "Add exponential backoff with jitter", "Reduce burst concurrency"]
    return "P3", "integration", 0.65, ["Insufficient evidence for a single root cause"], ["Capture the complete request/response", "Collect timestamps and request IDs", "Compare working and failing environments"]


def investigate(ticket: str, simulate_tool_failure: bool = False) -> Investigation:
    """Run a bounded synthetic investigation.

    ``simulate_tool_failure`` exists only for a clearly labeled portfolio demo
    scenario. It lets the failure/escalation path be tested without depending on
    a real external service.
    """
    started = time.perf_counter()
    run_id = f"run-{uuid.uuid4().hex[:10]}"
    ticket, was_truncated = bound_text(ticket)
    cid = _customer_id(ticket)

    customer = CUSTOMERS.get(cid, {"found": False})
    status = STATUS
    tool_errors: list[str] = []
    guardrails: list[str] = []

    if simulate_tool_failure:
        logs: list[dict] = []
        tool_errors.append("query_logs synthetic failure: diagnostic evidence unavailable")
        guardrails.append("tool_failure_requires_human_review")
    else:
        logs = [x for x in LOGS if x["customer_id"] == cid]

    if was_truncated:
        guardrails.append("input_truncated_to_configured_budget")

    severity, category, confidence, causes, steps = _classify(ticket, logs)

    forced = severity == "P1"
    reason = "P1 incidents require human escalation." if forced else "No deterministic high-risk signal detected."
    if forced:
        guardrails.append("p1_requires_human_approval")

    if tool_errors:
        forced = True
        reason = "A required diagnostic tool failed, so the agent cannot safely complete the investigation without human review."

    if not forced:
        for term in HIGH_RISK_TERMS:
            if term in ticket.lower():
                forced, reason = True, f"High-risk signal detected: {term}."
                guardrails.append("high_risk_signal_requires_human_approval")
                break

    kb_results = _search_kb(ticket)
    base_evidence = [
        {"source": "customer_lookup", "detail": customer},
        {"source": "service_status", "detail": status},
        *[{"source": "log_query", "detail": x} for x in logs[:2]],
        *kb_results,
    ]
    if tool_errors:
        base_evidence.append({"source": "tool_error", "detail": tool_errors[0]})

    reserve = 1 if forced else 0
    evidence = base_evidence[: max(0, MAX_EVIDENCE_ITEMS - reserve)]

    tools = ["search_knowledge_base", "lookup_customer", "check_service_status", "query_logs"]
    if forced:
        tools.append("create_escalation_preview")
        evidence.append({"source": "escalation_preview", "detail": {"preview_only": True, "severity": severity, "reason": reason, "external_action_taken": False}})

    action_status = "awaiting_human_approval" if forced else "recommendation_only_no_external_action"
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    decision_trace = [
        {"step": "input_guardrail", "result": "truncated" if was_truncated else "within_budget"},
        {"step": "evidence_collection", "result": f"{len(evidence)} bounded evidence items"},
        {"step": "classification", "result": {"severity": severity, "category": category, "confidence": confidence}},
        {"step": "policy", "result": {"human_approval_required": forced, "reason": reason}},
        {"step": "action", "result": action_status},
    ]

    return Investigation(
        severity=severity,
        category=category,
        confidence=confidence,
        likely_causes=causes,
        troubleshooting_steps=steps,
        escalate=forced,
        human_approval_required=forced,
        escalation_reason=reason,
        action_status=action_status,
        customer_response=f"I identified this as a {category} issue with {severity} priority. First, {steps[0].lower()}. I would validate the evidence before making a consequential change.",
        internal_notes=f"customer={cid}; category={category}; confidence={confidence:.2f}; evidence_items={len(evidence)}",
        evidence=evidence,
        tools_used=tools,
        tool_errors=tool_errors,
        guardrails_triggered=guardrails,
        decision_trace=decision_trace,
        telemetry={
            "request_id": run_id,
            "mode": "offline_deterministic",
            "request_chars": len(ticket),
            "approx_input_tokens": rough_token_estimate(ticket),
            "token_measurement": "rough_local_estimate_not_provider_usage",
            "context_items": len(evidence),
            "max_ticket_chars": MAX_TICKET_CHARS,
            "max_evidence_items": MAX_EVIDENCE_ITEMS,
            "latency_ms": latency_ms,
            "external_action_taken": False,
        },
    )
