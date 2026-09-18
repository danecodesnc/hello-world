from __future__ import annotations

SSO_SCIM_SCENARIO = {
    "customer_id": "CUST-303",
    "customer": "Acme Corp (synthetic)",
    "environment": "production",
    "saml_enabled": True,
    "idp_authentication": "successful",
    "saml_response_received": True,
    "nameid_email_mapping": "mismatch",
    "scim_enabled": True,
    "scim_provisioning_status": "partial_failure",
    "workspace_domain": "configured",
    "user_record": "missing_or_mismatched",
    "service_status": "operational",
    "platform_wide_outage": False,
    "request_id": "req-demo-sso-303",
}


def diagnose_sso_scim(ticket: str) -> dict:
    """Return a deterministic synthetic SSO/SCIM diagnosis.

    This models a generic enterprise identity workflow and does not represent
    TheyDo's internal authentication implementation.
    """
    checks = [
        "Verify the SAML NameID format matches the application's expected user identifier.",
        "Verify the email attribute mapping in the SAML assertion.",
        "Inspect the SAML assertion attributes for the affected and working users.",
        "Confirm the SCIM provisioning result and inspect any provisioning error.",
        "Confirm the affected user exists in the expected workspace.",
        "Verify domain-to-workspace mapping.",
        "Compare one affected user with one working user to isolate the mapping difference.",
    ]
    return {
        "category": "identity_sso_scim",
        "severity": "P2",
        "confidence": 0.95,
        "evidence": SSO_SCIM_SCENARIO.copy(),
        "likely_cause": "SAML identifier mapping and SCIM provisioning are inconsistent for the affected user.",
        "checks": checks,
        "reproduction_status": "Partially reproduced",
        "platform_outage_likely": False,
        "human_review_required": False,
        "external_action_taken": False,
        "note": "Synthetic generic enterprise identity scenario; not a representation of TheyDo internals.",
    }
