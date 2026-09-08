import re
from pydantic import BaseModel, Field

MAX_TICKET_CHARS = 6000
MAX_EVIDENCE_ITEMS = 6
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
    escalation_reason: str
    customer_response: str
    internal_notes: str
    evidence: list[dict]
    tools_used: list[str]


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


def investigate(ticket: str) -> Investigation:
    ticket = (ticket or "")[:MAX_TICKET_CHARS]
    cid = _customer_id(ticket)
    customer = CUSTOMERS.get(cid, {"found": False})
    logs = [x for x in LOGS if x["customer_id"] == cid]
    severity, category, confidence, causes, steps = _classify(ticket, logs)

    forced = severity == "P1"
    reason = "P1 incidents require human escalation." if forced else "No deterministic high-risk signal detected."
    if not forced:
        for term in HIGH_RISK_TERMS:
            if term in ticket.lower():
                forced, reason = True, f"High-risk signal detected: {term}."
                break

    evidence = [
        {"source": "customer_lookup", "detail": customer},
        {"source": "service_status", "detail": STATUS},
        *[{"source": "log_query", "detail": x} for x in logs[:2]],
        *_search_kb(ticket),
    ][:MAX_EVIDENCE_ITEMS]

    tools = ["search_knowledge_base", "lookup_customer", "check_service_status", "query_logs"]
    if forced:
        tools.append("create_escalation_preview")
        evidence.append({"source": "escalation_preview", "detail": {"preview_only": True, "severity": severity, "reason": reason}})

    return Investigation(
        severity=severity,
        category=category,
        confidence=confidence,
        likely_causes=causes,
        troubleshooting_steps=steps,
        escalate=forced,
        escalation_reason=reason,
        customer_response=f"I identified this as a {category} issue with {severity} priority. First, {steps[0].lower()}. I would validate the evidence before making a consequential change.",
        internal_notes=f"customer={cid}; category={category}; confidence={confidence:.2f}; evidence_items={len(evidence)}",
        evidence=evidence,
        tools_used=tools,
    )
