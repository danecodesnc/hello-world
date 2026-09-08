from dataclasses import dataclass, asdict


@dataclass
class RouteDecision:
    severity: str
    route: str
    human_approval_required: bool
    reason: str


def route_incident(ticket: str) -> dict:
    t = ticket.lower()
    if any(x in t for x in ["production down", "complete outage", "security breach", "data loss"]):
        d = RouteDecision("P1", "human_escalation_preview", True, "High-risk signal")
    elif any(x in t for x in ["401", "504", "multiple customers", "degraded"]):
        d = RouteDecision("P2", "senior_support_review", False, "Material technical impact")
    else:
        d = RouteDecision("P3", "standard_support", False, "No high-risk signal")
    return asdict(d)
