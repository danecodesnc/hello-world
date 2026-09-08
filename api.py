"""FastAPI surface for the public Agentic AI Support Portfolio."""
from __future__ import annotations

import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from incident_escalation_automation.router import route_incident

app = FastAPI(
    title="Dane Edwards — Agentic AI Support Portfolio API",
    version="1.0.0",
    description="Synthetic-data REST API for support investigation, incident routing, and API diagnostics.",
)


class InvestigationRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=6000)
    mode: Literal["offline", "live", "auto"] = "offline"


class IncidentRequest(BaseModel):
    ticket: str = Field(min_length=5, max_length=6000)


class DiagnosticRequest(BaseModel):
    status_code: int = Field(ge=100, le=599)
    url: str = "https://api.example.test/v1/resource"


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "portfolio": "agentic-ai-support",
        "live_llm_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/agent/investigate")
def agent_investigate(request: InvestigationRequest) -> dict:
    use_live = request.mode == "live" or (request.mode == "auto" and bool(os.getenv("OPENAI_API_KEY")))
    if not use_live:
        return {"mode": "offline", "result": investigate(request.ticket).model_dump()}

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="Live mode requires OPENAI_API_KEY; use mode='offline' for the public demo.")

    try:
        from atlas_support_agent.live_agent import run_live_investigation

        return run_live_investigation(request.ticket)
    except Exception as exc:  # keep public API error output bounded
        raise HTTPException(status_code=502, detail=f"Live LLM investigation failed: {type(exc).__name__}") from exc


@app.post("/incident/route")
def incident_route(request: IncidentRequest) -> dict:
    return route_incident(request.ticket)


@app.post("/api/diagnose")
def api_diagnose(request: DiagnosticRequest) -> dict:
    return diagnose(request.status_code, request.url)
