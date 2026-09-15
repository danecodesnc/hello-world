"""Credential-gated verification for the real OpenAI Responses API path.

This script intentionally fails unless a real OPENAI_API_KEY is present. It proves
that a provider response was received, at least one allow-listed function was
called, and token/latency telemetry was returned. It never prints the API key.
"""
from __future__ import annotations

import json
import os
import sys

from atlas_support_agent.live_agent import run_live_investigation

TICKET = (
    "Customer CUST-101 is receiving HTTP 401 errors after rotating production "
    "credentials. Postman works, but the production integration still fails. "
    "Gather evidence with the available synthetic support tools before answering."
)


def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("LIVE_LLM_VERIFICATION=BLOCKED: OPENAI_API_KEY is not configured.", file=sys.stderr)
        return 2

    result = run_live_investigation(TICKET)
    telemetry = result.get("telemetry", {})
    tools_used = result.get("tools_used", [])

    checks = {
        "live_mode": result.get("mode") == "live_llm",
        "provider_model_reported": bool(result.get("model")),
        "final_text_present": bool((result.get("final_text") or "").strip()),
        "function_call_observed": bool(tools_used),
        "input_tokens_recorded": int(telemetry.get("input_tokens", 0) or 0) > 0,
        "output_tokens_recorded": int(telemetry.get("output_tokens", 0) or 0) > 0,
        "latency_recorded": float(telemetry.get("latency_ms", 0) or 0) > 0,
    }

    passed = all(checks.values())
    safe_summary = {
        "verification": "PASS" if passed else "FAIL",
        "model": result.get("model"),
        "tools_used": tools_used,
        "telemetry": telemetry,
        "checks": checks,
        "final_text_preview": (result.get("final_text") or "")[:500],
    }
    print(json.dumps(safe_summary, indent=2))

    if passed:
        print("LIVE_LLM_VERIFICATION_COMPLETE")
        return 0

    print("LIVE_LLM_VERIFICATION_FAILED", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
