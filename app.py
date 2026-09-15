"""Recruiter-friendly browser UI for the public support portfolio."""
from __future__ import annotations

import os

import streamlit as st

from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from incident_escalation_automation.router import route_incident

st.set_page_config(page_title="Dane's AI Support Portfolio", page_icon="🛠️", layout="wide")

st.title("🛠️ Dane's AI Support & Automation Portfolio")
st.caption("Technical Support + APIs + Escalations + Applied AI Automation")
st.info("Everything in this demo is fictional. No real customer or employer data is used.")
st.markdown(
    "**Technical review:** [Source code](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio) · "
    "[60-second reviewer guide](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/REVIEWER_GUIDE.md) · "
    "[Verification record](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/VERIFICATION.md)"
)

st.markdown(
    """
### 👋 How to use this demo
**You do not need to know anything about programming.**

1. Pick one of the tabs below.
2. Leave the sample information exactly as it is, or change it if you want.
3. Click the big button.
4. Read the plain-English result.

The technical details are hidden unless you choose to open them.
"""
)

support_tab, incident_tab, api_tab, architecture_tab = st.tabs(
    ["🔎 Support Helper", "🚨 Incident Router", "🌐 API Error Helper", "🧠 How It Works"]
)

with support_tab:
    st.subheader("🔎 Support Helper")
    st.write("Imagine a customer says something is broken. This tool gathers clues and suggests what to do next.")
    st.success("Easy demo: leave the sample ticket alone and click **Analyze Support Ticket**.")

    sample = (
        "Customer CUST-101 is receiving HTTP 401 errors after rotating production credentials. "
        "Postman works, but the production integration still fails."
    )
    ticket = st.text_area("What did the customer report?", value=sample, height=140)

    live_enabled = bool(os.getenv("OPENAI_API_KEY"))
    mode = "Offline deterministic demo"
    with st.expander("⚙️ Advanced technical note"):
        if live_enabled:
            mode = st.radio(
                "Execution mode",
                ["Offline deterministic demo", "Live LLM tool-calling"],
            )
            st.caption("The public-safe offline path remains the recommended demonstration mode.")
        else:
            st.write(
                "The public demo intentionally uses the reproducible offline path. "
                "A credential-gated OpenAI Responses API tool-calling implementation is included in the source code and has a separate fail-closed verification gate."
            )

    if st.button("🔍 Analyze Support Ticket", type="primary", use_container_width=True):
        if mode.startswith("Live"):
            from atlas_support_agent.live_agent import run_live_investigation

            with st.spinner("Gathering clues and investigating..."):
                live_result = run_live_investigation(ticket)
            st.success("Investigation complete.")
            st.json(live_result)
        else:
            result = investigate(ticket).model_dump()
            st.success("Investigation complete.")

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
            if result["escalate"]:
                st.warning(f'Yes. {result["escalation_reason"]}')
            else:
                st.success("Not automatically. The evidence does not trigger a high-risk escalation rule.")

            st.markdown("### 💬 Example customer explanation")
            st.write(result["customer_response"])

            with st.expander("🔧 Technical details for engineers"):
                st.json(result)

with incident_tab:
    st.subheader("🚨 Incident Router")
    st.write("This tool decides how urgently an incident should be handled and whether a human must approve the next step.")
    st.success("Easy demo: leave the sample alone and click **Route Incident**.")

    incident = st.text_area(
        "What is happening?",
        value="Multiple customers report degraded API performance and repeated HTTP 504 responses.",
        height=120,
    )
    if st.button("🚦 Route Incident", type="primary", use_container_width=True):
        result = route_incident(incident)
        st.success("Routing decision complete.")

        c1, c2 = st.columns(2)
        c1.metric("Priority", result["severity"])
        c2.metric("Route", result["route"].replace("_", " ").title())

        st.markdown("### 👤 Human approval needed?")
        if result["human_approval_required"]:
            st.warning("Yes. A person must review this before a consequential action is taken.")
        else:
            st.success("No special approval is required by the current rule.")

        st.write("**Why:**", result["reason"])
        with st.expander("🔧 Technical details for engineers"):
            st.json(result)

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
    st.write("The simple idea: the program gathers clues, follows safety rules, and either suggests a solution or asks a human to step in.")
    st.markdown(
        """
```text
Customer problem
      ↓
AI support helper
      ↓
Gather approved clues
  • knowledge
  • customer context
  • service status
  • logs
      ↓
Apply safety rules
      ↓
 ┌───────────────┐
 ↓               ↓
Suggested       Human review
solution        when risk is high
```

### The grown-up technical version

- Python application
- Streamlit browser interface
- FastAPI REST backend
- allow-listed tools only
- retrieval-grounded evidence
- structured outputs
- bounded context / token controls
- deterministic high-risk guardrails
- human approval for consequential actions
- optional OpenAI Responses API function calling
- real n8n workflow import + execution verified in GitHub Actions
- regression tests and GitHub Actions CI
        """
    )
