from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


@dataclass
class RouteDecision:
    severity: str
    route: str
    human_approval_required: bool
    reason: str


def route_incident(ticket: str) -> dict:
    t = (ticket or "").lower()
    if any(x in t for x in ["production down", "complete outage", "security breach", "data loss"]):
        d = RouteDecision("P1", "human_escalation_preview", True, "High-risk signal")
    elif any(x in t for x in ["401", "504", "multiple customers", "degraded"]):
        d = RouteDecision("P2", "senior_support_review", False, "Material technical impact")
    else:
        d = RouteDecision("P3", "standard_support", False, "No high-risk signal")
    return asdict(d)


def apply_human_decision(
    route_result: dict,
    decision: Literal["approve", "reject", "escalate"],
) -> dict:
    """Record a portfolio-only human decision without taking an external action."""
    if decision not in {"approve", "reject", "escalate"}:
        raise ValueError("decision must be approve, reject, or escalate")

    if decision == "approve":
        status = "approved_for_next_step" if route_result.get("human_approval_required") else "acknowledged"
    elif decision == "reject":
        status = "rejected_no_action"
    else:
        status = "escalated_to_human_owner"

    return {
        "decision": decision,
        "decision_status": status,
        "severity": route_result.get("severity"),
        "route": route_result.get("route"),
        "human_approval_required": bool(route_result.get("human_approval_required")),
        "external_action_taken": False,
        "note": "Portfolio demo only. This records the human decision but does not modify Jira, Slack, CRM, or a customer system.",
    }
