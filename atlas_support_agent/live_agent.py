"""Optional live LLM investigation loop using the OpenAI Responses API.

The public portfolio remains fully runnable without this file. Live mode is enabled
only when OPENAI_API_KEY is present. All callable tools operate on synthetic data.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

from openai import OpenAI

from atlas_support_agent import agent as offline

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
MAX_TOOL_ROUNDS = 4
MAX_OUTPUT_TOKENS = 1000

TOOLS = [
    {
        "type": "function",
        "name": "search_knowledge_base",
        "description": "Search the synthetic support knowledge base for evidence relevant to the ticket.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Support issue or error to search for."}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "lookup_customer",
        "description": "Look up synthetic customer metadata by customer ID.",
        "parameters": {
            "type": "object",
            "properties": {"customer_id": {"type": "string", "description": "Synthetic ID such as CUST-101."}},
            "required": ["customer_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "check_service_status",
        "description": "Read the synthetic platform service-status record.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function",
        "name": "query_logs",
        "description": "Retrieve bounded synthetic log events for one customer.",
        "parameters": {
            "type": "object",
            "properties": {"customer_id": {"type": "string", "description": "Synthetic ID such as CUST-101."}},
            "required": ["customer_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "create_escalation_preview",
        "description": "Create a preview-only escalation record. This never changes an external system.",
        "parameters": {
            "type": "object",
            "properties": {
                "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
                "reason": {"type": "string"},
            },
            "required": ["severity", "reason"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def _run_tool(name: str, args: dict[str, Any]) -> Any:
    if name == "search_knowledge_base":
        return offline._search_kb(str(args["query"]))
    if name == "lookup_customer":
        return offline.CUSTOMERS.get(str(args["customer_id"]).upper(), {"found": False})
    if name == "check_service_status":
        return offline.STATUS
    if name == "query_logs":
        cid = str(args["customer_id"]).upper()
        return [row for row in offline.LOGS if row["customer_id"] == cid][:3]
    if name == "create_escalation_preview":
        return {
            "preview_only": True,
            "severity": args["severity"],
            "reason": str(args["reason"])[:500],
            "external_action_taken": False,
        }
    raise ValueError(f"Tool is not allow-listed: {name}")


def run_live_investigation(ticket: str) -> dict[str, Any]:
    """Run a bounded live investigation and return output + observability metadata."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    bounded_ticket = (ticket or "")[: offline.MAX_TICKET_CHARS]
    client = OpenAI(api_key=api_key)
    input_items: list[Any] = [
        {
            "role": "system",
            "content": (
                "You are a support-engineering investigation agent. Use only the supplied synthetic tools and evidence. "
                "Do not claim an external action occurred. Gather evidence before drawing conclusions. "
                "If the issue is P1 or high-risk, use create_escalation_preview. Keep the final answer concise and structured."
            ),
        },
        {"role": "user", "content": bounded_ticket},
    ]

    started = time.perf_counter()
    tools_used: list[str] = []
    input_tokens = 0
    output_tokens = 0
    final_text = ""

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.responses.create(
            model=MODEL,
            input=input_items,
            tools=TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

        usage = getattr(response, "usage", None)
        input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
        output_tokens += int(getattr(usage, "output_tokens", 0) or 0)
        input_items += list(response.output)

        calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
        if not calls:
            final_text = response.output_text
            break

        for call in calls:
            name = call.name
            args = json.loads(call.arguments or "{}")
            result = _run_tool(name, args)
            tools_used.append(name)
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result),
                }
            )
    else:
        final_text = "Tool-round limit reached before a final model response was produced."

    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    return {
        "mode": "live_llm",
        "model": MODEL,
        "final_text": final_text,
        "tools_used": tools_used,
        "telemetry": {
            "tool_round_limit": MAX_TOOL_ROUNDS,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
        },
    }
