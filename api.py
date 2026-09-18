"""FastAPI surface for the public AI Support Operations Portfolio."""
from __future__ import annotations

import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from incident_escalation_automation.router import apply_human_decision, route_incident
from support_operations import (
    SYNTHETIC_TICKETS,
    detect_duplicate_patterns,
    format_engineering_handoff,
    generate_customer_update,
    generate_engineering_handoff,
    get_support_metrics,
)

app = FastAPI(
    title="Dane Edwards — AI Support Operations Portfolio API",
    version="2.0.0",
    description="Synthetic-data REST API for support investigation, engineering handoff, customer communication, incident routing, support operations, and API diagnostics.",
)


class InvestigationRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=6000)
    mode: Literal["offline", "live", "auto"] = "offline"
    simulate_tool_failure: bool = False


class TicketRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=6000)
    simulate_tool_failure: bool = False


class IncidentRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=6000)


class IncidentDecisionRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=6000)
    decision: Literal["approve", "reject", "escalate"]


class DiagnosticRequest(BaseModel):
    status_code: int = Field(ge=100, le=599)
    url: str = "https://api.example.test/v1/resource"


class DuplicateTicket(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=3, max_length=2000)
    severity: str = "P3"
    category: str = "Unclassified"


class DuplicateRequest(BaseModel):
    tickets: list[DuplicateTicket] | None = None


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "portfolio": "ai-support-operations",
        "live_llm_configured": bool(os.getenv("OPENAI_API_KEY")),
        "external_actions_enabled": False,
    }


@app.post("/agent/investigate")
def agent_investigate(request: InvestigationRequest) -> dict:
    use_live = request.mode == "live" or (request.mode == "auto" and bool(os.getenv("OPENAI_API_KEY")))
    if not use_live:
        return {
            "mode": "offline",
            "result": investigate(request.ticket, simulate_tool_failure=request.simulate_tool_failure).model_dump(),
        }

    if request.simulate_tool_failure:
        raise HTTPException(status_code=400, detail="simulate_tool_failure is supported only by the offline synthetic demo path.")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="Live mode requires OPENAI_API_KEY; use mode='offline' for the public demo.")

    try:
        from atlas_support_agent.live_agent import run_live_investigation

        return run_live_investigation(request.ticket)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Live LLM investigation failed: {type(exc).__name__}") from exc


@app.post("/engineering/handoff")
def engineering_handoff(request: TicketRequest) -> dict:
    result = investigate(request.ticket, simulate_tool_failure=request.simulate_tool_failure)
    report = generate_engineering_handoff(request.ticket, result)
    return {"report": report, "copyable_text": format_engineering_handoff(report)}


@app.post("/support/customer-update")
def customer_update(request: TicketRequest) -> dict:
    result = investigate(request.ticket, simulate_tool_failure=request.simulate_tool_failure)
    return {"customer_update": generate_customer_update(request.ticket, result), "external_action_taken": False}


@app.post("/support/duplicates")
def support_duplicates(request: DuplicateRequest) -> dict:
    rows = [ticket.model_dump() for ticket in request.tickets] if request.tickets else SYNTHETIC_TICKETS
    return {"patterns": detect_duplicate_patterns(rows), "method": "deterministic explainable rules"}


@app.get("/support/metrics")
def support_metrics() -> dict:
    return get_support_metrics()


@app.post("/incident/route")
def incident_route(request: IncidentRequest) -> dict:
    return route_incident(request.ticket)


@app.post("/incident/decision")
def incident_decision(request: IncidentDecisionRequest) -> dict:
    route_result = route_incident(request.ticket)
    return apply_human_decision(route_result, request.decision)


@app.post("/api/diagnose")
def api_diagnose(request: DiagnosticRequest) -> dict:
    return diagnose(request.status_code, request.url)
