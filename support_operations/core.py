from __future__ import annotations

import re
from collections import Counter
from typing import Any

SYNTHETIC_TICKETS = [
    {"id": "TKT-1001", "text": "Production API returns HTTP 401 after API key rotation.", "severity": "P2", "category": "Authentication"},
    {"id": "TKT-1002", "text": "New production credentials are rejected with 401 Unauthorized.", "severity": "P2", "category": "Authentication"},
    {"id": "TKT-1003", "text": "Authentication stopped after replacing the production secret.", "severity": "P2", "category": "Authentication"},
    {"id": "TKT-1004", "text": "Dashboard page loads slowly for one user.", "severity": "P3", "category": "Configuration"},
    {"id": "TKT-1005", "text": "SAML user authenticates at the IdP but cannot enter the workspace.", "severity": "P2", "category": "SSO / Provisioning"},
    {"id": "TKT-1006", "text": "SCIM-created user is missing from the expected workspace.", "severity": "P2", "category": "SSO / Provisioning"},
    {"id": "TKT-1007", "text": "Multiple production requests return HTTP 504 upstream timeout.", "severity": "P2", "category": "API Timeout"},
    {"id": "TKT-1008", "text": "Second customer reports repeated 504 responses with request IDs.", "severity": "P2", "category": "API Timeout"},
    {"id": "TKT-1009", "text": "Production down - complete outage for all customers.", "severity": "P1", "category": "Platform Availability"},
    {"id": "TKT-1010", "text": "Customer needs help configuring a non-production webhook.", "severity": "P3", "category": "Configuration"},
]


def _dict_result(result: Any) -> dict:
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return dict(result)


def detect_missing_information(ticket: str) -> list[str]:
    """Return evidence fields that are not explicitly present in the customer report."""
    t = (ticket or "").lower()
    missing: list[str] = []

    if not re.search(r"(req(?:uest)?[-_ ]?id|req-[a-z0-9-]+)", t):
        missing.append("request ID")
    if not re.search(r"(\b\d{1,2}:\d{2}\b|\b20\d{2}-\d{2}-\d{2}\b|timestamp)", t):
        missing.append("timestamp")
    if not re.search(r"(https?://|/api/|endpoint|url)", t):
        missing.append("endpoint / URL")
    if not any(word in t for word in ("production", "prod", "staging", "sandbox", "test environment", "workspace")):
        missing.append("environment")
    if not re.search(r"\b(?:400|401|403|404|409|429|500|502|503|504)\b|error|unauthorized|timeout|access", t):
        missing.append("exact error / response")
    if not any(word in t for word in ("after", "when", "steps", "reproduce", "rotat", "enabled", "returning")):
        missing.append("reproduction steps")

    return missing


def reproduction_status(ticket: str, result: Any) -> dict:
    payload = _dict_result(result)
    if payload.get("tool_errors"):
        return {
            "status": "Unable to reproduce with available evidence",
            "reason": "A required diagnostic source failed, so the evidence set is incomplete.",
        }

    missing = detect_missing_information(ticket)
    category = payload.get("category")
    evidence = payload.get("evidence", [])
    has_log = any(item.get("source") == "log_query" for item in evidence if isinstance(item, dict))

    if category in {"authentication", "performance", "identity_sso_scim"} and has_log and len(missing) <= 3:
        return {
            "status": "Reproduced",
            "reason": "The synthetic evidence contains a matching technical failure that supports the reported behavior.",
        }
    if has_log:
        return {
            "status": "Partially reproduced",
            "reason": "A related failure is present in the synthetic evidence, but the customer report is missing important reproduction context.",
        }
    if len(missing) >= 4:
        return {
            "status": "Unable to reproduce with available evidence",
            "reason": "The report does not contain enough concrete request context to reproduce the issue safely.",
        }
    return {
        "status": "Not reproduced",
        "reason": "The current evidence does not contain a matching reproducible failure.",
    }


def get_technical_evidence(ticket: str, result: Any) -> dict:
    payload = _dict_result(result)
    t = ticket.lower()
    log_records = [
        item.get("detail", {})
        for item in payload.get("evidence", [])
        if isinstance(item, dict) and item.get("source") == "log_query"
    ]
    status_records = [
        item.get("detail", {})
        for item in payload.get("evidence", [])
        if isinstance(item, dict) and item.get("source") == "service_status"
    ]
    first_log = log_records[0] if log_records else {}
    service_state = (status_records[0] or {}).get("state", "unknown") if status_records else "unknown"

    endpoint = "Not provided"
    endpoint_match = re.search(r"(https?://\S+|/api/[\w\-/]+)", ticket)
    if endpoint_match:
        endpoint = endpoint_match.group(1).rstrip(".,)")

    browser = "Chrome (synthetic demo)" if ("browser" in t or "saml" in t or "workspace" in t) else "Not provided"
    os_name = "Windows 11 (synthetic demo)" if browser != "Not provided" else "Not provided"

    return {
        "browser": browser,
        "operating_system": os_name,
        "environment": "Production" if ("production" in t or "prod" in t) else "Not explicitly provided",
        "request_method": "POST" if payload.get("category") in {"authentication", "identity_sso_scim"} else "Not provided",
        "endpoint": endpoint if endpoint != "Not provided" else ("/api/v1/auth (synthetic)" if payload.get("category") == "authentication" else "Not provided"),
        "http_response": f'{first_log.get("status")} {first_log.get("message")}' if first_log else "Not captured",
        "request_id": first_log.get("request_id", "Not provided"),
        "timestamp": "Not provided",
        "console_error": "None captured in synthetic scenario",
        "network_result": first_log.get("message", "No matching network failure captured"),
        "service_status": service_state,
        "reproduction_status": reproduction_status(ticket, payload)["status"],
    }


def generate_engineering_handoff(ticket: str, result: Any) -> dict:
    payload = _dict_result(result)
    missing = detect_missing_information(ticket)
    reproduction = reproduction_status(ticket, payload)
    tech = get_technical_evidence(ticket, payload)
    category = payload.get("category", "integration")
    severity = payload.get("severity", "P3")
    causes = payload.get("likely_causes") or ["No single root-cause hypothesis is supported yet."]
    steps = payload.get("troubleshooting_steps") or []

    environment = tech["environment"]
    if environment == "Not explicitly provided":
        for item in payload.get("evidence", []):
            if item.get("source") == "customer_lookup" and isinstance(item.get("detail"), dict):
                raw = item["detail"].get("environment")
                if raw:
                    environment = str(raw).title()
                    break

    status_text = "Escalation preview awaiting human review" if payload.get("human_approval_required") else "Support investigation in progress; no external action taken"

    title_map = {
        "authentication": "Authentication failure after credential/configuration change",
        "performance": "Repeated API timeout / latency failure",
        "identity_sso_scim": "SAML SSO / SCIM provisioning access failure",
        "availability": "Platform availability incident",
    }

    return {
        "issue_title": title_map.get(category, f"{category.replace('_', ' ').title()} support issue"),
        "severity": severity,
        "environment": environment,
        "customer_impact": "Customer workflow is blocked or degraded." if severity in {"P1", "P2"} else "Limited customer impact reported.",
        "affected_customers": "Multiple / broad" if severity == "P1" or "multiple customers" in ticket.lower() else "1 synthetic customer unless otherwise stated",
        "expected_behavior": "The requested customer workflow should complete successfully with valid configuration and credentials.",
        "actual_behavior": ticket.strip(),
        "reproduction_status": reproduction["status"],
        "reproduction_reason": reproduction["reason"],
        "reproduction_steps": steps[:4] if reproduction["status"] != "Unable to reproduce with available evidence" else ["Collect the missing request context first.", "Repeat the exact customer workflow in the stated environment.", "Capture request/response evidence and request ID."],
        "technical_evidence": tech,
        "suspected_component": category.replace("_", " ").title(),
        "root_cause_hypothesis": causes[0],
        "confidence": payload.get("confidence", 0),
        "workarounds_attempted": ["No customer-impacting change is performed by this public demo."],
        "recommended_engineering_investigation": steps,
        "missing_information": missing,
        "escalation_reason": payload.get("escalation_reason", ""),
        "customer_facing_status": status_text,
        "external_action_taken": False,
    }


def format_engineering_handoff(report: dict) -> str:
    evidence = report["technical_evidence"]
    missing = report["missing_information"]
    steps = report["reproduction_steps"]
    engineering = report["recommended_engineering_investigation"]
    return "\n".join([
        f'Issue: {report["issue_title"]}',
        f'Severity: {report["severity"]}',
        f'Environment: {report["environment"]}',
        f'Customer impact: {report["customer_impact"]}',
        f'Affected customers: {report["affected_customers"]}',
        "",
        f'Expected behavior: {report["expected_behavior"]}',
        f'Actual behavior: {report["actual_behavior"]}',
        "",
        f'Reproduction: {report["reproduction_status"]}',
        *[f'{i}. {step}' for i, step in enumerate(steps, 1)],
        "",
        "Technical evidence:",
        f'- HTTP/network result: {evidence["http_response"]}',
        f'- Request ID: {evidence["request_id"]}',
        f'- Service status: {evidence["service_status"]}',
        f'- Browser: {evidence["browser"]}',
        f'- Endpoint: {evidence["endpoint"]}',
        "",
        f'Root-cause hypothesis: {report["root_cause_hypothesis"]}',
        f'Confidence: {round(float(report["confidence"]) * 100)}%',
        "",
        "Recommended engineering investigation:",
        *[f'- {item}' for item in engineering],
        "",
        "Missing information:",
        *([f'- {item}' for item in missing] if missing else ["- None identified by the deterministic demo rules."]),
        "",
        f'Escalation reason: {report["escalation_reason"]}',
        f'Customer-facing status: {report["customer_facing_status"]}',
        "External action taken: false",
    ])


def generate_customer_update(ticket: str, result: Any) -> str:
    payload = _dict_result(result)
    missing = detect_missing_information(ticket)
    category = payload.get("category", "technical").replace("_", " ")
    steps = payload.get("troubleshooting_steps") or []
    next_step = steps[0] if steps else "collect additional technical evidence"

    lines = [
        "Thanks for the details. I reviewed the information available so far.",
        f"The issue currently appears related to {category}, but I am keeping the conclusion tied to the evidence we have rather than assuming a root cause.",
        f"Next I would {next_step.lower().rstrip('.')}.",
    ]
    if payload.get("human_approval_required"):
        lines.append("Because this case meets an escalation or evidence-quality boundary, I would route it for human review before any consequential action.")
    if missing:
        lines.append("To continue the investigation, please provide: " + ", ".join(missing[:5]) + ".")
    lines.append("No changes have been made to your environment by this demo.")
    return " ".join(lines)


def detect_duplicate_patterns(tickets: list[dict] | None = None) -> list[dict]:
    rows = tickets or SYNTHETIC_TICKETS
    groups = [
        {
            "name": "Authentication / Credential Rotation",
            "keywords": ("401", "credential", "api key", "secret", "authentication"),
            "shared_characteristics": ["production environment", "HTTP 401 / authentication failure", "credential or secret change", "same authentication workflow"],
        },
        {
            "name": "SSO / Provisioning",
            "keywords": ("saml", "scim", "workspace", "idp", "provision"),
            "shared_characteristics": ["enterprise identity workflow", "authentication/provisioning boundary", "workspace access"],
        },
        {
            "name": "API Timeout",
            "keywords": ("504", "timeout", "latency", "upstream"),
            "shared_characteristics": ["API request path", "timeout response", "production performance impact"],
        },
    ]
    output = []
    for definition in groups:
        matches = []
        for row in rows:
            text = row["text"].lower()
            score = sum(1 for keyword in definition["keywords"] if keyword in text)
            if score >= 1:
                matches.append(row)
        if len(matches) >= 2:
            confidence = min(0.98, 0.70 + (0.07 * len(matches)))
            output.append({
                "pattern": definition["name"],
                "related_tickets": [row["id"] for row in matches],
                "count": len(matches),
                "confidence": round(confidence, 2),
                "shared_characteristics": definition["shared_characteristics"],
                "reason": "Grouped by transparent deterministic keyword/category rules; this is not presented as a trained ML classifier.",
                "suggested_action": "Consolidate the related reports into one primary investigation while preserving each customer impact record.",
            })
    return output


def get_support_metrics(tickets: list[dict] | None = None) -> dict:
    rows = tickets or SYNTHETIC_TICKETS
    sev = Counter(row["severity"] for row in rows)
    categories = Counter(row["category"] for row in rows)
    patterns = detect_duplicate_patterns(rows)
    return {
        "label": "Demo metrics — synthetic data",
        "open_issues": len(rows),
        "p1": sev["P1"],
        "p2": sev["P2"],
        "p3": sev["P3"],
        "first_response_sla_pct": 96,
        "median_first_response_minutes": 18,
        "human_review_cases": 2,
        "automated_triage_pct": 80,
        "duplicate_groups_detected": len(patterns),
        "api_related_cases": sum(1 for row in rows if row["category"] in {"Authentication", "API Timeout"}),
        "identity_sso_cases": sum(1 for row in rows if row["category"] == "SSO / Provisioning"),
        "unresolved_escalations": 1,
        "average_investigation_confidence_pct": 87,
        "top_issue_categories": [{"category": name, "count": count} for name, count in categories.most_common()],
        "repeating_patterns": patterns,
    }
