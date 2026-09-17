"""Shared runtime controls for the support-agent portfolio.

These helpers keep limits and telemetry explicit without pretending that rough
local estimates are provider-reported token counts.
"""
from __future__ import annotations

import math
import os
from typing import Optional

MAX_TICKET_CHARS = int(os.getenv("MAX_TICKET_CHARS", "6000"))
MAX_EVIDENCE_ITEMS = int(os.getenv("MAX_EVIDENCE_ITEMS", "6"))
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "4"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "1000"))
APPROX_INPUT_TOKEN_BUDGET = int(os.getenv("APPROX_INPUT_TOKEN_BUDGET", "12000"))
MAX_CONTEXT_ITEMS = int(os.getenv("MAX_CONTEXT_ITEMS", "24"))


def rough_token_estimate(text: str) -> int:
    """Return an intentionally rough local estimate (~4 chars/token).

    This is used only for preflight budgeting in offline/demo mode. It is never
    labeled as provider-reported usage.
    """
    return max(1, math.ceil(len(text or "") / 4))


def bound_text(text: str) -> tuple[str, bool]:
    """Bound user text by both character and approximate token budgets."""
    raw = text or ""
    char_cap_from_token_budget = APPROX_INPUT_TOKEN_BUDGET * 4
    cap = min(MAX_TICKET_CHARS, char_cap_from_token_budget)
    bounded = raw[:cap]
    return bounded, len(raw) > len(bounded)


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> Optional[float]:
    """Estimate provider cost only when rates are explicitly configured.

    Pricing changes over time, so the repository deliberately avoids hard-coded
    model pricing. Set OPENAI_INPUT_COST_PER_1M_USD and
    OPENAI_OUTPUT_COST_PER_1M_USD to enable this calculation.
    """
    try:
        input_rate = float(os.getenv("OPENAI_INPUT_COST_PER_1M_USD", "0"))
        output_rate = float(os.getenv("OPENAI_OUTPUT_COST_PER_1M_USD", "0"))
    except ValueError:
        return None
    if input_rate <= 0 and output_rate <= 0:
        return None
    cost = (input_tokens / 1_000_000) * input_rate + (output_tokens / 1_000_000) * output_rate
    return round(cost, 6)
