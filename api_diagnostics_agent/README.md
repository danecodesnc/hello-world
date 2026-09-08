# API Diagnostics Agent

A focused troubleshooting utility that converts common HTTP failures into a structured investigation plan.

## Supported status codes

- **400** — request validation
- **401** — authentication
- **403** — authorization
- **404** — route/resource
- **429** — rate limiting
- **500** — server-side error
- **503** — service availability
- **504** — upstream/gateway timeout

## Output

For each failure, the utility returns:

- category;
- plain-English explanation;
- verification checklist;
- escalation recommendation;
- safe example cURL command using an environment-variable token placeholder.

## Example

```python
from api_diagnostics_agent.diagnose import diagnose

result = diagnose(401)
print(result)
```

The 401 path emphasizes comparing the failing Authorization header against a known-good Postman request, verifying the production secret source, and confirming credential-rotation propagation.

## Why this project exists

It connects the agentic-AI portfolio to practical API support work: HTTP semantics, Postman/cURL troubleshooting, environment differences, rate limits, request IDs, retries, and escalation-quality evidence.

## Safety

The default URL is a reserved synthetic example domain, credentials are represented only as `$API_TOKEN`, and no real customer or former-employer endpoints are included.