from incident_escalation_automation.router import route_incident
from api_diagnostics_agent.diagnose import diagnose


def test_incident_router_p1():
    r = route_incident("production down - complete outage")
    assert r["severity"] == "P1"
    assert r["human_approval_required"] is True


def test_api_401():
    r = diagnose(401)
    assert r["category"] == "authentication"
    assert r["escalate"] is False


def test_api_503_escalates():
    assert diagnose(503)["escalate"] is True
