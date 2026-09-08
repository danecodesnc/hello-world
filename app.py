"""Recruiter-friendly browser UI for the public support portfolio."""
from __future__ import annotations

import os

import streamlit as st

from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from incident_escalation_automation.router import route_incident

st.set_page_config(page_title="Agentic AI Support Portfolio", page_icon="🛠️", layout="wide")

st.title("Agentic AI Support & Automation Portfolio")
st.caption("Dane Edwards — Technical Support + APIs + Escalations + Applied AI Automation")
st.info("All customers, logs, tickets, service data, and product examples in this demo are fictional/synthetic.")

support_tab, incident_tab, api_tab, architecture_tab = st.tabs(
    ["Support Agent", "Incident Router", "API Diagnostics", "Architecture"]
)

with support_tab:
    st.subheader("Atlas Support AI Agent")
    sample = (
        "Customer CUST-101 is receiving HTTP 401 errors after rotating production credentials. "
        "Postman works, but the production integration still fails."
    )
    ticket = st.text_area("Support ticket", value=sample, height=140)
    mode = st.radio(
        "Execution mode",
        ["Offline deterministic demo", "Live LLM tool-calling (requires OPENAI_API_KEY)"],
        horizontal=True,
    )
    if st.button("Investigate ticket", type="primary"):
        if mode.startswith("Live"):
            if not os.getenv("OPENAI_API_KEY"):
                st.error("OPENAI_API_KEY is not configured. Use the offline demo or configure a local key.")
            else:
                from atlas_support_agent.live_agent import run_live_investigation

                with st.spinner("Running bounded live investigation..."):
                    st.json(run_live_investigation(ticket))
        else:
            st.json(investigate(ticket).model_dump())

with incident_tab:
    st.subheader("Incident & Escalation Automation")
    incident = st.text_area(
        "Incident signal",
        value="Multiple customers report degraded API performance and repeated HTTP 504 responses.",
        height=120,
    )
    if st.button("Route incident"):
        st.json(route_incident(incident))
    st.caption("P1/high-risk routes are preview-only and require human approval.")

with api_tab:
    st.subheader("API Diagnostics Agent")
    status = st.selectbox("HTTP status", [400, 401, 403, 404, 429, 500, 503, 504], index=1)
    url = st.text_input("Synthetic API URL", value="https://api.example.test/v1/resource")
    if st.button("Diagnose API failure"):
        st.json(diagnose(int(status), url))

with architecture_tab:
    st.subheader("Controlled agent architecture")
    st.markdown(
        """
```text
Support Ticket / API Failure
            ↓
   Streamlit / FastAPI
            ↓
       Support Agent
      ↙    ↓    ↘
     KB  Customer  Logs/Status
      ↘    ↓    ↙
     Evidence-grounded reasoning
            ↓
   Deterministic guardrails
       ↙             ↘
 Resolution     Human escalation preview
```

**Design principles**
- allow-listed tools only
- bounded context and output
- synthetic public data
- deterministic P1/high-risk policy
- human approval for consequential actions
- optional live LLM function calling
- offline path remains fully demonstrable without credentials
        """
    )
