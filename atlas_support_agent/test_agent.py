from atlas_support_agent.agent import investigate


def test_401_authentication():
    r = investigate("Customer CUST-101 gets HTTP 401 after credential rotation; Postman works.")
    assert r.category == "authentication"
    assert r.severity == "P2"
    assert r.confidence >= 0.9
    assert "query_logs" in r.tools_used


def test_p1_guardrail():
    r = investigate("Customer CUST-101 reports production down and complete outage.")
    assert r.severity == "P1"
    assert r.escalate is True
    assert "create_escalation_preview" in r.tools_used
