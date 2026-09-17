"""Recruiter-friendly browser UI for the public support portfolio."""
from __future__ import annotations

import os

import streamlit as st

from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from incident_escalation_automation.router import apply_human_decision, route_incident

st.set_page_config(page_title="Dane's AI Support Portfolio", page_icon="🛠️", layout="wide")

SUPPORT_SCENARIOS = {
    "401 credential rotation — recommended first demo": {
        "ticket": "Customer CUST-101 is receiving HTTP 401 errors after rotating production credentials. Postman works, but the production integration still fails.",
        "simulate_tool_failure": False,
        "purpose": "Shows evidence gathering, API troubleshooting, retrieval, classification, and a high-confidence recommendation.",
    },
    "Ambiguous integration issue": {
        "ticket": "Customer CUST-101 says the integration behaves differently between test and production, but no error code or request ID was provided.",
        "simulate_tool_failure": False,
        "purpose": "Shows a lower-confidence result when the evidence is incomplete.",
    },
    "Low-confidence unknown issue": {
        "ticket": "Customer CUST-202 reports intermittent unexpected behavior with no timestamps, request IDs, or reproducible steps.",
        "simulate_tool_failure": False,
        "purpose": "Shows that the agent does not invent a precise root cause when evidence is weak.",
    },
    "P1 complete outage — human escalation": {
        "ticket": "Production down - complete outage for all customers. Preserve evidence and escalate immediately.",
        "simulate_tool_failure": False,
        "purpose": "Shows deterministic high-risk policy and a human-approval boundary.",
    },
    "Synthetic diagnostic-tool failure": {
        "ticket": "Customer CUST-101 reports an authentication failure, but the diagnostic log tool is unavailable.",
        "simulate_tool_failure": True,
        "purpose": "Exercises the explicit failure path: incomplete evidence forces human review instead of a confident automated conclusion.",
    },
    "Malformed / too-short input": {
        "ticket": "bad",
        "simulate_tool_failure": False,
        "purpose": "Demonstrates front-end input validation before the investigation runs.",
    },
    "Complex multi-tool timeout case": {
        "ticket": "Customer CUST-202 reports repeated HTTP 504 timeouts in production. Multiple requests are affected and request IDs are available for investigation.",
        "simulate_tool_failure": False,
        "purpose": "Shows customer context, service status, logs, knowledge retrieval, classification, and bounded evidence in one run.",
    },
}

INCIDENT_SCENARIOS = {
    "P2 degraded API": "Multiple customers report degraded API performance and repeated HTTP 504 responses.",
    "P1 outage requiring approval": "Production down - complete outage for all customers.",
    "P3 routine support": "One customer has a configuration question with no production impact.",
}

st.title("🛠️ Dane's AI Support & Automation Portfolio")
st.caption("Technical Support + APIs + Escalations + Applied AI Automation")
st.info("Everything in this demo is fictional. No real customer or employer data is used.")
st.markdown(
    "**Technical review:** [Source code](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio) · "
    "[60-second reviewer guide](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/REVIEWER_GUIDE.md) · "
    "[Architecture](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/ARCHITECTURE.md) · "
    "[Verification record](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/VERIFICATION.md)"
)

st.markdown(
    """
### 👋 How to use this demo
**You do not need to know anything about programming.**

1. Pick a scenario.
2. Click the large action button.
3. Read the plain-English result.
4. Open **AI Usage & Observability** if you want to see tools, limits, timing, and guardrails.

The public demo takes **no real external action**. High-risk paths stop for human review.
"""
)

support_tab, incident_tab, api_tab, architecture_tab = st.tabs(
    ["🔎 Support Helper", "🚨 Incident Router", "🌐 API Error Helper", "🧠 How It Works"]
)

with support_tab:
    st.subheader("🔎 Support Helper")
    st.write("Imagine a customer says something is broken. The agent gathers approved clues, applies safety rules, and suggests what to do next.")

    scenario_name = st.selectbox("Choose a built-in demo scenario", list(SUPPORT_SCENARIOS.keys()))
    scenario = SUPPORT_SCENARIOS[scenario_name]
    st.caption(scenario["purpose"])
    ticket = st.text_area(
        "What did the customer report?",
        value=scenario["ticket"],
        height=140,
        key=f"support_ticket::{scenario_name}",
    )

    live_enabled = bool(os.getenv("OPENAI_API_KEY"))
    mode = "Offline deterministic demo"
    with st.expander("⚙️ Advanced technical options"):
        if live_enabled:
            mode = st.radio(
                "Execution mode",
                ["Offline deterministic demo", "Live LLM tool-calling"],
            )
            st.caption("The offline path is recommended for a reproducible interview demo. Live mode requires a private credential.")
        else:
            st.write(
                "The public deployment intentionally uses the reproducible offline path. "
                "A credential-gated OpenAI Responses API tool-calling implementation is included in the repository with a separate fail-closed verification gate."
            )

    if st.button("🔍 Analyze Support Ticket", type="primary", use_container_width=True):
        if len(ticket.strip()) < 5:
            st.session_state.pop("support_result", None)
            st.error("Input validation blocked this request: please provide at least 5 characters of support context.")
        elif mode.startswith("Live") and scenario["simulate_tool_failure"]:
            st.warning("The synthetic failure scenario is intentionally implemented in the offline demo path. Running that path instead.")
            st.session_state["support_result"] = {
                "mode": "offline",
                "result": investigate(ticket, simulate_tool_failure=True).model_dump(),
            }
        elif mode.startswith("Live"):
            from atlas_support_agent.live_agent import run_live_investigation

            with st.spinner("Gathering approved evidence and investigating..."):
                st.session_state["support_result"] = run_live_investigation(ticket)
        else:
            st.session_state["support_result"] = {
                "mode": "offline",
                "result": investigate(ticket, simulate_tool_failure=scenario["simulate_tool_failure"]).model_dump(),
            }

    support_payload = st.session_state.get("support_result")
    if support_payload:
        st.success("Investigation complete.")
        if support_payload.get("mode") == "offline":
            result = support_payload["result"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Priority", result["severity"])
            c2.metric("Problem type", result["category"].replace("_", " ").title())
            c3.metric("Confidence", f'{round(result["confidence"] * 100)}%')

            st.markdown("### 💡 What probably happened")
            for item in result["likely_causes"]:
                st.write(f"• {item}")

            st.markdown("### ✅ What I would try next")
            for number, item in enumerate(result["troubleshooting_steps"], start=1):
                st.write(f"{number}. {item}")

            st.markdown("### 👤 Does a person need to step in?")
            if result["human_approval_required"]:
                st.warning(f'Yes. {result["escalation_reason"]}')
                st.caption("The portfolio creates an escalation preview only. It cannot modify a real external system.")
            else:
                st.success("Not automatically. The evidence does not trigger a high-risk escalation rule.")

            if result["tool_errors"]:
                st.error("A diagnostic tool failed safely, so the workflow stopped short of an automated conclusion and routed to human review.")

            st.markdown("### 💬 Example customer explanation")
            st.write(result["customer_response"])

            with st.expander("📊 AI Usage & Observability"):
                telemetry = result["telemetry"]
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Approx. input tokens", telemetry["approx_input_tokens"])
                m2.metric("Context items", telemetry["context_items"])
                m3.metric("Latency", f'{telemetry["latency_ms"]} ms')
                m4.metric("External actions", "0")
                st.caption("Offline token count is a rough local estimate, not provider-reported model usage.")
                st.write("**Request ID:**", telemetry["request_id"])
                st.write("**Tools used:**", ", ".join(result["tools_used"]))
                st.write("**Guardrails triggered:**", ", ".join(result["guardrails_triggered"]) or "None")
                st.write("**Action status:**", result["action_status"])
                st.markdown("**Decision trace**")
                st.json(result["decision_trace"])

            with st.expander("🔧 Full technical result for engineers"):
                st.json(result)
        else:
            st.markdown("### Live model result")
            st.write(support_payload.get("final_text") or "No final model text returned.")
            telemetry = support_payload.get("telemetry", {})
            with st.expander("📊 AI Usage & Observability", expanded=True):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Input tokens", telemetry.get("input_tokens", 0))
                m2.metric("Output tokens", telemetry.get("output_tokens", 0))
                m3.metric("Context docs", telemetry.get("context_documents", 0))
                m4.metric("Latency", f'{telemetry.get("latency_ms", 0)} ms')
                st.write("**Model:**", support_payload.get("model"))
                st.write("**Tools used:**", ", ".join(support_payload.get("tools_used", [])) or "None")
                st.write("**Cached tokens:**", telemetry.get("cached_tokens", 0))
                cost = telemetry.get("estimated_cost_usd")
                st.write("**Estimated cost:**", f"${cost:.6f}" if isinstance(cost, (int, float)) else "Not calculated; no pricing rates configured")
                st.write("**Cost measurement:**", telemetry.get("cost_measurement"))
                st.json(support_payload.get("tool_events", []))

with incident_tab:
    st.subheader("🚨 Incident Router")
    st.write("This workflow decides how urgently an incident should be handled and demonstrates a human approval boundary for high-risk events.")

    incident_scenario = st.selectbox("Choose an incident scenario", list(INCIDENT_SCENARIOS.keys()))
    incident = st.text_area(
        "What is happening?",
        value=INCIDENT_SCENARIOS[incident_scenario],
        height=120,
        key=f"incident::{incident_scenario}",
    )

    if st.button("🚦 Route Incident", type="primary", use_container_width=True):
        st.session_state["incident_result"] = route_incident(incident)
        st.session_state.pop("incident_human_decision", None)

    incident_result = st.session_state.get("incident_result")
    if incident_result:
        st.success("Routing decision complete.")
        c1, c2 = st.columns(2)
        c1.metric("Priority", incident_result["severity"])
        c2.metric("Route", incident_result["route"].replace("_", " ").title())

        st.markdown("### 👤 Human approval needed?")
        if incident_result["human_approval_required"]:
            st.warning("Yes. A person must explicitly approve, reject, or escalate before the workflow can move beyond the preview stage.")
            b1, b2, b3 = st.columns(3)
            if b1.button("✅ Approve preview", use_container_width=True):
                st.session_state["incident_human_decision"] = apply_human_decision(incident_result, "approve")
            if b2.button("❌ Reject", use_container_width=True):
                st.session_state["incident_human_decision"] = apply_human_decision(incident_result, "reject")
            if b3.button("⬆️ Escalate to owner", use_container_width=True):
                st.session_state["incident_human_decision"] = apply_human_decision(incident_result, "escalate")
        else:
            st.success("No special approval is required by the current deterministic policy.")

        st.write("**Why:**", incident_result["reason"])
        human_decision = st.session_state.get("incident_human_decision")
        if human_decision:
            st.markdown("### Human decision record")
            st.json(human_decision)
            st.info("This is a portfolio-only decision record. No Jira, Slack, CRM, or customer system was changed.")

        with st.expander("🔧 Technical routing result"):
            st.json(incident_result)

with api_tab:
    st.subheader("🌐 API Error Helper")
    st.write("APIs are how computer programs talk to each other. Pick an error number and this tool explains what it means and what to check.")
    st.success("Easy demo: keep **401** selected and click **Explain This API Error**.")

    status = st.selectbox(
        "Choose an HTTP error number",
        [400, 401, 403, 404, 429, 500, 503, 504],
        index=1,
        help="401 is a common authentication error and makes a good demo.",
    )
    url = st.text_input("Example API address", value="https://api.example.test/v1/resource")

    if st.button("🌐 Explain This API Error", type="primary", use_container_width=True):
        result = diagnose(int(status), url)
        st.success("Diagnosis complete.")

        st.markdown(f'### What **{result["status"]}** means')
        st.write(result["explanation"])
        st.write("**Problem type:**", result["category"].replace("_", " ").title())

        st.markdown("### ✅ What I would check")
        for number, item in enumerate(result["checks"], start=1):
            st.write(f"{number}. {item}")

        if result["escalate"]:
            st.warning("This type of error may need escalation if the basic checks do not resolve it.")
        else:
            st.info("Start with the checks above before escalating.")

        with st.expander("🔧 Technical details and example cURL command"):
            st.code(result["curl_example"], language="bash")
            st.json(result)

with architecture_tab:
    st.subheader("🧠 How It Works")
    st.write("The program separates probabilistic AI reasoning from deterministic Python policy and keeps consequential actions behind a human boundary.")
    st.markdown(
        """
```text
User / support event
        ↓
Application / API
        ↓
Agent routing
        ↓
Approved tools only
  • knowledge retrieval
  • customer context
  • service status
  • bounded logs
        ↓
Observations / evidence
        ↓
Decision + confidence
        ↓
Deterministic guardrails
        ↓
 ┌───────────────────┬──────────────────────┐
 ↓                   ↓
Recommendation      Human approval / escalation
(no external write) (preview only)
        ↓                   ↓
        └──── logging / telemetry ──────────┘
```

### Engineering controls demonstrated

- Python application logic and deterministic business rules
- Streamlit browser interface
- FastAPI REST backend + OpenAPI/Postman surface
- allow-listed function tools only
- retrieval-grounded synthetic evidence
- structured Pydantic outputs
- bounded ticket, evidence, context-item, tool-round, and output-token limits
- provider-reported token telemetry in credential-gated live mode
- clearly labeled rough token estimates in offline mode
- configurable cost estimation without hard-coded model pricing
- deterministic P1/high-risk guardrails
- synthetic tool-failure path that fails toward human review
- interactive human approval/reject/escalate record with zero external writes
- optional OpenAI Responses API function calling
- executable n8n workflow verified in GitHub Actions
- regression tests and CI
        """
    )
