from types import SimpleNamespace

from atlas_support_agent import live_agent


class FakeResponses:
    def __init__(self):
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            tool_call = SimpleNamespace(
                type="function_call",
                name="lookup_customer",
                arguments='{"customer_id":"CUST-101"}',
                call_id="call-demo-1",
            )
            return SimpleNamespace(
                output=[tool_call],
                output_text="",
                usage=SimpleNamespace(input_tokens=100, output_tokens=20),
            )
        return SimpleNamespace(
            output=[],
            output_text="Synthetic live-loop verification complete.",
            usage=SimpleNamespace(input_tokens=50, output_tokens=10),
        )


class FakeClient:
    def __init__(self, api_key=None, **kwargs):
        self.api_key = api_key
        self.options = kwargs
        self.responses = FakeResponses()


def test_function_call_loop_and_telemetry(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    monkeypatch.setattr(live_agent, "OpenAI", FakeClient)

    result = live_agent.run_live_investigation(
        "Customer CUST-101 gets HTTP 401 after credential rotation."
    )

    assert result["mode"] == "live_llm"
    assert result["request_id"].startswith("live-")
    assert result["final_text"] == "Synthetic live-loop verification complete."
    assert result["tools_used"] == ["lookup_customer"]
    assert result["tool_events"][0]["status"] == "ok"
    assert result["telemetry"]["input_tokens"] == 150
    assert result["telemetry"]["output_tokens"] == 30
    assert result["telemetry"]["total_tokens"] == 180
    assert result["telemetry"]["cached_tokens"] == 0
    assert result["telemetry"]["latency_ms"] >= 0
    assert result["telemetry"]["tool_round_limit"] == live_agent.MAX_TOOL_ROUNDS
    assert result["telemetry"]["max_output_tokens"] == live_agent.MAX_OUTPUT_TOKENS
    assert result["telemetry"]["external_action_taken"] is False
