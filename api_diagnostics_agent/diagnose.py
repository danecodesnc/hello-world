from dataclasses import dataclass, asdict


@dataclass
class Diagnosis:
    status: int
    category: str
    explanation: str
    checks: list[str]
    escalate: bool
    curl_example: str


RULES = {
    400: ("request_validation", "The server rejected the request as invalid.", ["Validate JSON syntax/schema", "Check required fields and data types", "Confirm Content-Type"], False),
    401: ("authentication", "The request did not present an accepted credential.", ["Compare Authorization header to a known-good Postman request", "Verify the production secret source", "Confirm credential rotation propagated"], False),
    403: ("authorization", "Authentication may be valid, but the caller lacks permission.", ["Verify role/scope", "Confirm resource ownership", "Check environment/tenant"], False),
    404: ("resource_or_route", "The route or resource was not found.", ["Verify base URL and API version", "Check resource identifier", "Confirm environment"], False),
    429: ("rate_limit", "The caller exceeded an API rate limit.", ["Inspect Retry-After", "Use exponential backoff with jitter", "Reduce concurrency"], False),
    500: ("server_error", "The service encountered an unexpected server-side error.", ["Capture request ID", "Check service status", "Minimize reproducible request"], True),
    503: ("availability", "The service is temporarily unavailable or overloaded.", ["Check service status", "Capture request IDs/timestamps", "Use bounded retries only for safe/idempotent operations"], True),
    504: ("performance", "A gateway timed out waiting for an upstream dependency.", ["Capture request ID and duration", "Check upstream/service health", "Review retry/backoff behavior"], True),
}


def diagnose(status: int, url: str = "https://api.example.test/v1/resource") -> dict:
    category, explanation, checks, escalate = RULES.get(status, ("unknown", "No rule is defined for this status.", ["Capture the complete request/response", "Check documentation", "Escalate with request ID"], True))
    curl = f'curl -i -X GET "{url}" -H "Authorization: Bearer $API_TOKEN" -H "Accept: application/json"'
    return asdict(Diagnosis(status, category, explanation, checks, escalate, curl))
