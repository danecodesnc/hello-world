from fastapi.testclient import TestClient

from api import app
from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from incident_escalation_automation.router import route_incident

client = TestClient(app)


def test_support_agent_401():
    result = investigate("Customer CUST-101 has HTTP 401 after credential rotation; Postman works.")
    assert result.category == "authentication"
    assert result.severity == "P2"
    assert "query_logs" in result.tools_used


def test_support_agent_p1_guardrail():
    result = investigate("Production down - complete outage for all customers")
    assert result.severity == "P1"
    assert result.escalate is True
    assert "create_escalation_preview" in result.tools_used


def test_incident_router_p1():
    result = route_incident("production down - complete outage")
    assert result["severity"] == "P1"
    assert result["human_approval_required"] is True


def test_api_401_diagnosis():
    result = diagnose(401)
    assert result["category"] == "authentication"
    assert result["escalate"] is False


def test_api_503_escalates():
    assert diagnose(503)["escalate"] is True


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_investigation_endpoint_offline():
    response = client.post(
        "/agent/investigate",
        json={"ticket": "Customer CUST-101 reports HTTP 401 after credential rotation.", "mode": "offline"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "offline"
    assert payload["result"]["category"] == "authentication"


def test_diagnostic_endpoint():
    response = client.post("/api/diagnose", json={"status_code": 504})
    assert response.status_code == 200
    assert response.json()["category"] == "performance"
