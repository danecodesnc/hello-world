"""Reusable synthetic support-operations helpers for the public portfolio."""

from .core import (
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

__all__ = [
    "SYNTHETIC_TICKETS",
    "detect_duplicate_patterns",
    "detect_missing_information",
    "format_engineering_handoff",
    "generate_customer_update",
    "generate_engineering_handoff",
    "get_support_metrics",
    "get_technical_evidence",
    "reproduction_status",
]
