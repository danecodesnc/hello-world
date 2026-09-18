"""Recruiter-friendly browser UI for the public AI Support Operations portfolio."""
from __future__ import annotations

import os

import streamlit as st

from api_diagnostics_agent.diagnose import diagnose
from atlas_support_agent.agent import investigate
from incident_escalation_automation.router import apply_human_decision, route_incident
from support_operations import (
    SYNTHETIC_TICKETS,
    detect_duplicate_patterns,
    detect_missing_information,
    format_engineering_handoff,
    generate_customer_update,
    generate_engineering_handoff,
    get_support_metrics,
    get_technical_evidence,
    reproduction_status,
)

st.set_page_config(page_title="Dane's AI Support Operations Demo", page_icon="🛠️", layout="wide")

SUPPORT_SCENARIOS = {
    "401 credential rotation — recommended first demo": {
        "ticket": "Customer CUST-101 reports HTTP 401 in production after rotating API credentials. Postman works, but the production integration still fails at /api/v1/auth.",
        "simulate_tool_failure": False,
        "purpose": "Shows API troubleshooting, synthetic logs, reproducible evidence, customer communication, and an engineering-ready handoff.",
    },
    "SAML SSO / SCIM provisioning failure": {
        "ticket": "Acme Corp enabled SAML SSO in its production workspace. Users authenticate successfully with the identity provider but receive an access error when returning to the application. Some recently provisioned users are missing from the workspace.",
        "simulate_tool_failure": False,
        "purpose": "Shows a generic enterprise identity investigation without implying access to TheyDo internals.",
    },
    "Ambiguous integration issue": {
        "ticket": "Customer CUST-202 says the integration behaves differently between test and production, but no error code or request ID was provided.",
        "simulate_tool_failure": False,
        "purpose": "Shows missing-information detection and restrained conclusions when customer evidence is incomplete.",
    },
    "Low-confidence unknown issue": {
        "ticket": "Customer CUST-202 reports intermittent unexpected behavior with no timestamps, request IDs, endpoints, or reproducible steps.",
        "simulate_tool_failure": False,
        "purpose": "Shows that the workflow asks for evidence instead of inventing a root cause.",
    },
    "P1 complete outage — human escalation": {
        "ticket": "Production down - complete outage for all customers. Preserve evidence and escalate immediately.",
        "simulate_tool_failure": False,
        "purpose": "Shows deterministic high-risk policy and a human-approval boundary.",
    },
    "Synthetic diagnostic-tool failure": {
        "ticket": "Customer CUST-101 reports an authentication failure in production, but the diagnostic log tool is unavailable.",
        "simulate_tool_failure": True,
        "purpose": "Shows failure reducing autonomy: incomplete evidence forces human review.",
    },
    "Complex 504 timeout case": {
        "ticket": "Customer CUST-202 reports repeated HTTP 504 timeouts in production at /api/v1/resource. Multiple requests are affected and request IDs are available for investigation.",
        "simulate_tool_failure": False,
        "purpose": "Shows customer context, service status, logs, knowledge retrieval, and bounded evidence.",
    },
}

INCIDENT_SCENARIOS = {
    "P2 degraded API": "Multiple customers report degraded API performance and repeated HTTP 504 responses.",
    "P1 outage requiring approval": "Production down - complete outage for all customers.",
    "P3 routine support": "One customer has a configuration question with no production impact.",
}

st.title("🛠️ AI-Powered Technical Support Operations Demo")
st.caption("Dane Edwards — technical issue investigation, API diagnostics, engineering escalation, workflow automation, and human-controlled AI")
st.info("Public portfolio using fictional/synthetic data only. No real customer systems are connected and no external writes are enabled.")
st.markdown(
    "**Workflow:** Customer Report → Gather Evidence → Investigate → Reproduce → Recommend Fix → Customer Update → Engineering Handoff → Human Review"
)
st.markdown(
    "**Technical review:** "
    "[Source code](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio) · "
    "[60-second reviewer guide](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/REVIEWER_GUIDE.md) · "
    "[Architecture](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/ARCHITECTURE.md) · "
    "[Verification](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/VERIFICATION.md)"
)

with st.expander("👋 20-second orientation", expanded=True):
    st.write(
        "Choose a synthetic customer issue and click Analyze. The default view shows the support outcome first; "
        "deeper implementation details, telemetry, and raw JSON remain collapsed for technical reviewers."
    )

investigation_tab, handoff_tab, incident_tab, api_tab, operations_tab, architecture_tab = st.tabs(
    [
        "🔎 Customer Issue Investigation",
        "🐛 Engineering Handoff",
        "🚨 Incident & Escalation",
        "🌐 API Diagnostics",
        "📊 Support Operations",
        "🧠 Architecture & Automation",
    ]
)

with investigation_tab:
    st.subheader("🔎 Customer Issue Investigation")
    st.write("Turn a customer report into bounded evidence, a support diagnosis, a customer update, and an engineering-ready handoff.")

    scenario_name = st.selectbox("Choose a built-in scenario", list(SUPPORT_SCENARIOS.keys()), key="support_scenario")
    scenario = SUPPORT_SCENARIOS[scenario_name]
    st.caption(scenario["purpose"])
    ticket = st.text_area("What did the customer report?", value=scenario["ticket"], height=145, key=f"support_ticket::{scenario_name}")

    live_enabled = bool(os.getenv("OPENAI_API_KEY"))
    mode = "Offline deterministic demo"
    with st.expander("⚙️ Advanced execution options"):
        st.write("The public interview path is deterministic and reproducible. It is not labeled as LLM inference.")
        if live_enabled:
            mode = st.radio("Execution mode", ["Offline deterministic demo", "Live LLM tool-calling"])
            st.caption("Live mode is optional and credential-gated. High-risk policy remains deterministic.")
        else:
            st.caption("No OpenAI credential is required for the public demo. Optional live tool-calling code remains in the repository.")

    if st.button("🔍 Analyze Customer Issue", type="primary", use_container_width=True):
        st.session_state.pop("generated_handoff", None)
        st.session_state.pop("generated_customer_update", None)
        if len(ticket.strip()) < 5:
            st.session_state.pop("support_result", None)
            st.error("Please provide at least 5 characters of support context.")
        elif mode.startswith("Live") and scenario["simulate_tool_failure"]:
            st.warning("The synthetic failure scenario uses the reproducible offline path.")
            st.session_state["support_result"] = {"mode": "offline", "ticket": ticket, "result": investigate(ticket, simulate_tool_failure=True).model_dump()}
        elif mode.startswith("Live"):
            from atlas_support_agent.live_agent import run_live_investigation

            with st.spinner("Gathering approved evidence and investigating..."):
                st.session_state["support_result"] = {"mode": "live", "ticket": ticket, "result": run_live_investigation(ticket)}
        else:
            st.session_state["support_result"] = {
                "mode": "offline",
                "ticket": ticket,
                "result": investigate(ticket, simulate_tool_failure=scenario["simulate_tool_failure"]).model_dump(),
            }

    support_payload = st.session_state.get("support_result")
    if support_payload:
        st.success("Investigation complete.")
        if support_payload["mode"] == "offline":
            result = support_payload["result"]
            current_ticket = support_payload["ticket"]
            repro = reproduction_status(current_ticket, result)
            missing = detect_missing_information(current_ticket)
            technical = get_technical_evidence(current_ticket, result)

            st.markdown("### Executive summary")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Priority", result["severity"])
            c2.metric("Category", result["category"].replace("_", " ").title())
            c3.metric("Confidence", f'{round(result["confidence"] * 100)}%')
            c4.metric("Reproduction", repro["status"])

            st.markdown("### What the customer reported")
            st.write(current_ticket)

            st.markdown("### Evidence collected")
            evidence_labels = []
            for item in result["evidence"]:
                source = item.get("source", "evidence").replace("_", " ").title()
                if source not in evidence_labels:
                    evidence_labels.append(source)
            st.write(" • ".join(evidence_labels) if evidence_labels else "No evidence available.")

            st.markdown("### Technical findings")
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Service", str(technical["service_status"]).title())
            e2.metric("HTTP / network", technical["http_response"])
            e3.metric("Request ID", technical["request_id"])
            e4.metric("Environment", technical["environment"])
            with st.expander("Technical evidence details"):
                st.json(technical)

            st.markdown("### Most Likely Cause")
            for item in result["likely_causes"]:
                st.write(f"• {item}")

            st.markdown("### Recommended troubleshooting")
            for number, item in enumerate(result["troubleshooting_steps"], start=1):
                st.write(f"{number}. {item}")

            st.markdown("### Information needed before deeper investigation")
            if missing:
                for item in missing:
                    st.write(f"• {item}")
            else:
                st.success("No obvious evidence fields are missing from the synthetic customer report.")
            st.caption(repro["reason"])

            col_customer, col_engineering = st.columns(2)
            if col_customer.button("💬 Generate Customer Update", use_container_width=True):
                st.session_state["generated_customer_update"] = generate_customer_update(current_ticket, result)
            if col_engineering.button("🐛 Generate Engineering Handoff", use_container_width=True):
                st.session_state["generated_handoff"] = generate_engineering_handoff(current_ticket, result)

            if st.session_state.get("generated_customer_update"):
                st.markdown("### Customer response")
                st.code(st.session_state["generated_customer_update"], language=None)

            if st.session_state.get("generated_handoff"):
                st.markdown("### Engineering handoff")
                handoff = st.session_state["generated_handoff"]
                st.code(format_engineering_handoff(handoff), language=None)

            st.markdown("### Human Review / Escalation")
            if result["human_approval_required"]:
                st.warning(result["escalation_reason"])
                st.caption("The workflow creates a preview only. A human retains control and the public demo performs no external write.")
            else:
                st.success("No deterministic high-risk rule currently requires human approval.")

            with st.expander("📊 Advanced observability"):
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

            with st.expander("🔧 Raw technical result"):
                st.json(result)
        else:
            live_result = support_payload["result"]
            st.markdown("### Live model result")
            st.write(live_result.get("final_text") or "No final model text returned.")
            with st.expander("📊 Live observability", expanded=True):
                st.json(live_result.get("telemetry", {}))
                st.write("**Tools used:**", ", ".join(live_result.get("tools_used", [])) or "None")

with handoff_tab:
    st.subheader("🐛 Engineering Handoff")
    st.write("Convert a support report into a reproducible, evidence-based QA/Engineering handoff instead of throwing a vague ticket over the wall.")
    handoff_ticket = st.text_area(
        "Synthetic issue",
        value=SUPPORT_SCENARIOS["401 credential rotation — recommended first demo"]["ticket"],
        height=130,
        key="handoff_ticket",
    )
    if st.button("Generate Engineering-Ready Bug Report", type="primary", use_container_width=True):
        handoff_result = investigate(handoff_ticket).model_dump()
        st.session_state["standalone_handoff"] = generate_engineering_handoff(handoff_ticket, handoff_result)
    if st.session_state.get("standalone_handoff"):
        standalone = st.session_state["standalone_handoff"]
        h1, h2, h3 = st.columns(3)
        h1.metric("Severity", standalone["severity"])
        h2.metric("Reproduction", standalone["reproduction_status"])
        h3.metric("Confidence", f'{round(standalone["confidence"] * 100)}%')
        st.code(format_engineering_handoff(standalone), language=None)
        with st.expander("Structured handoff JSON"):
            st.json(standalone)

with incident_tab:
    st.subheader("🚨 Incident & Escalation")
    st.write("Automation can identify urgency, but high-risk decisions remain behind a human approval boundary.")
    incident_scenario = st.selectbox("Choose an incident scenario", list(INCIDENT_SCENARIOS.keys()))
    incident = st.text_area("What is happening?", value=INCIDENT_SCENARIOS[incident_scenario], height=115, key=f"incident::{incident_scenario}")

    if st.button("🚦 Route Incident", type="primary", use_container_width=True):
        st.session_state["incident_result"] = route_incident(incident)
        st.session_state.pop("incident_human_decision", None)

    incident_result = st.session_state.get("incident_result")
    if incident_result:
        sev = incident_result["severity"]
        impact = "Broad customer impact" if sev == "P1" else ("Material customer impact" if sev == "P2" else "Limited impact")
        scope = "All / multiple customers" if ("all customers" in incident.lower() or "multiple customers" in incident.lower()) else "Single / unspecified customer"
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Severity", sev)
        c2.metric("Customer impact", impact)
        c3.metric("Scope", scope)
        c4.metric("Service status", "Needs incident review" if sev == "P1" else "Operational / degraded evidence")
        st.write("**Escalation route:**", incident_result["route"].replace("_", " ").title())
        st.write("**Reason:**", incident_result["reason"])
        st.write("**External action status:** No external action taken")

        st.markdown("### Human approval requirement")
        if incident_result["human_approval_required"]:
            st.warning("Human approval is required before the workflow could move beyond the preview stage.")
            b1, b2, b3 = st.columns(3)
            if b1.button("✅ Approve preview", use_container_width=True):
                st.session_state["incident_human_decision"] = apply_human_decision(incident_result, "approve")
            if b2.button("❌ Reject", use_container_width=True):
                st.session_state["incident_human_decision"] = apply_human_decision(incident_result, "reject")
            if b3.button("⬆️ Escalate to owner", use_container_width=True):
                st.session_state["incident_human_decision"] = apply_human_decision(incident_result, "escalate")
        else:
            st.success("No special approval is required by the current deterministic policy.")

        if st.session_state.get("incident_human_decision"):
            st.json(st.session_state["incident_human_decision"])
            st.info("Portfolio-only decision record. external_action_taken remains false.")

with api_tab:
    st.subheader("🌐 API Diagnostics")
    st.write("Explain common HTTP failures and give a support engineer a concrete first troubleshooting path.")
    status = st.selectbox("Choose an HTTP status", [400, 401, 403, 404, 429, 500, 503, 504], index=1)
    url = st.text_input("Example API address", value="https://api.example.test/v1/resource")
    if st.button("🌐 Diagnose API Error", type="primary", use_container_width=True):
        st.session_state["api_result"] = diagnose(int(status), url)
    if st.session_state.get("api_result"):
        api_result = st.session_state["api_result"]
        st.markdown(f'### {api_result["status"]} — {api_result["category"].replace("_", " ").title()}')
        st.write(api_result["explanation"])
        st.markdown("### What I would check")
        for number, item in enumerate(api_result["checks"], start=1):
            st.write(f"{number}. {item}")
        with st.expander("Technical details and example cURL"):
            st.code(api_result["curl_example"], language="bash")
            st.json(api_result)

with operations_tab:
    st.subheader("📊 Support Operations")
    metrics = get_support_metrics()
    st.info(metrics["label"])
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Open issues", metrics["open_issues"])
    a2.metric("First-response SLA", f'{metrics["first_response_sla_pct"]}%')
    a3.metric("Median first response", f'{metrics["median_first_response_minutes"]} min')
    a4.metric("Automated triage", f'{metrics["automated_triage_pct"]}%')
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("P1 / P2 / P3", f'{metrics["p1"]} / {metrics["p2"]} / {metrics["p3"]}')
    b2.metric("Human review cases", metrics["human_review_cases"])
    b3.metric("Duplicate groups", metrics["duplicate_groups_detected"])
    b4.metric("Avg. confidence", f'{metrics["average_investigation_confidence_pct"]}%')

    st.markdown("### What is breaking most often?")
    st.table(metrics["top_issue_categories"])

    st.markdown("### Repeating patterns / possible duplicates")
    patterns = detect_duplicate_patterns()
    for pattern in patterns:
        with st.container(border=True):
            p1, p2 = st.columns([2, 1])
            p1.markdown(f'**{pattern["pattern"]}**')
            p2.metric("Confidence", f'{round(pattern["confidence"] * 100)}%')
            st.write("Related tickets:", ", ".join(pattern["related_tickets"]))
            st.write("Shared characteristics:", " • ".join(pattern["shared_characteristics"]))
            st.write("Suggested action:", pattern["suggested_action"])
            st.caption(pattern["reason"])

    with st.expander("Synthetic ticket dataset"):
        st.table(SYNTHETIC_TICKETS)

with architecture_tab:
    st.subheader("🧠 Architecture & Automation")
    st.write("The project deliberately separates probabilistic model behavior from deterministic application controls.")

    st.markdown("### Support workflow")
    st.code(
        """Customer report
    ↓
Bounded evidence gathering
    ↓
Investigation + reproduction assessment
    ↓
Customer communication ──────┐
    ↓                        │
Engineering handoff          │
    ↓                        │
Deterministic guardrails     │
    ↓                        │
Human review when required ←─┘
    ↓
Telemetry / decision trace""",
        language=None,
    )

    st.markdown("### Workflow Automation — n8n")
    st.code(
        """Support event
    ↓
Normalize input
    ↓
Classify
    ↓
Apply deterministic guardrail
    ↓
Select route
    ↓
Human decision where required
    ↓
Observability""",
        language=None,
    )
    st.write(
        "The repository contains an importable n8n workflow and GitHub Actions verification that runs it in the official n8n container. "
        "It demonstrates orchestration only; it does not perform production writes."
    )
    st.markdown(
        "[n8n workflow](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/incident_escalation_automation/01_support_escalation_router.n8n.json) · "
        "[n8n verification workflow](https://github.com/danecodesnc/dane-agentic-ai-support-portfolio/blob/master/.github/workflows/n8n-verification.yml)"
    )

    st.markdown("### Offline demo vs. optional live LLM")
    left, right = st.columns(2)
    with left:
        st.markdown("**Offline deterministic demo**")
        st.write("Reproducible Python workflow using bounded synthetic data. This is the default public interview path and is not labeled as LLM inference.")
        st.write("Python owns severity, tool permissions, validation, execution limits, escalation boundaries, and external-write policy.")
    with right:
        st.markdown("**Optional live LLM mode**")
        st.write("Credential-gated tool-calling path for natural-language interpretation, evidence synthesis, and approved tool selection.")
        st.write("Consequential policy remains outside the model.")

    st.markdown("### Production gaps kept explicit")
    st.write(
        "A real deployment would still need enterprise SSO/RBAC, tenant isolation, durable audit storage, PII controls, production connectors, "
        "ACL-aware retrieval, stronger prompt-injection defenses, rate limiting, formal evaluations, load testing, and service-level monitoring."
    )
