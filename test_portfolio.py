from fastapi.testclient import TestClient

from api import app
from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from atlas_support_agent.runtime import rough_token_estimate
from incident_escalation_automation.router import apply_human_decision, route_incident

client = TestClient(app)


def test_support_agent_401():
    result = investigate("Customer CUST-101 has HTTP 401 after credential rotation; Postman works.")
    assert result.category == "authentication"
    assert result.severity == "P2"
    assert "query_logs" in result.tools_used
    assert result.human_approval_required is False


def test_support_agent_p1_guardrail():
    result = investigate("Production down - complete outage for all customers")
    assert result.severity == "P1"
    assert result.escalate is True
    assert result.human_approval_required is True
    assert "create_escalation_preview" in result.tools_used
    assert "p1_requires_human_approval" in result.guardrails_triggered


def test_support_agent_tool_failure_fails_to_human_review():
    result = investigate("Customer CUST-101 reports authentication trouble.", simulate_tool_failure=True)
    assert result.human_approval_required is True
    assert result.tool_errors
    assert result.action_status == "awaiting_human_approval"
    assert result.telemetry["external_action_taken"] is False


def test_support_agent_observability_is_bounded_and_labeled():
    result = investigate("Customer CUST-202 reports repeated 504 timeout errors.")
    assert result.telemetry["request_id"].startswith("run-")
    assert result.telemetry["approx_input_tokens"] >= 1
    assert result.telemetry["token_measurement"] == "rough_local_estimate_not_provider_usage"
    assert result.telemetry["context_items"] <= result.telemetry["max_evidence_items"]
    assert len(result.decision_trace) >= 4


def test_rough_token_estimate():
    assert rough_token_estimate("abcd") == 1
    assert rough_token_estimate("abcde") == 2


def test_incident_router_p1():
    result = route_incident("production down - complete outage")
    assert result["severity"] == "P1"
    assert result["human_approval_required"] is True


def test_human_decision_never_takes_external_action():
    route = route_incident("production down - complete outage")
    result = apply_human_decision(route, "approve")
    assert result["decision_status"] == "approved_for_next_step"
    assert result["external_action_taken"] is False


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
    assert response.json()["external_actions_enabled"] is False


def test_investigation_endpoint_offline():
    response = client.post(
        "/agent/investigate",
        json={"ticket": "Customer CUST-101 reports HTTP 401 after credential rotation.", "mode": "offline"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "offline"
    assert payload["result"]["category"] == "authentication"


def test_investigation_endpoint_tool_failure_demo():
    response = client.post(
        "/agent/investigate",
        json={
            "ticket": "Customer CUST-101 reports authentication trouble.",
            "mode": "offline",
            "simulate_tool_failure": True,
        },
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["human_approval_required"] is True
    assert result["tool_errors"]


def test_investigation_endpoint_rejects_too_short_input():
    response = client.post("/agent/investigate", json={"ticket": "bad", "mode": "offline"})
    assert response.status_code == 422


def test_incident_decision_endpoint():
    response = client.post(
        "/incident/decision",
        json={"ticket": "production down - complete outage", "decision": "escalate"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["decision_status"] == "escalated_to_human_owner"
    assert payload["external_action_taken"] is False


def test_diagnostic_endpoint():
    response = client.post("/api/diagnose", json={"status_code": 504})
    assert response.status_code == 200
    assert response.json()["category"] == "performance"
