"""Optional programmatic LLM adapter for the public portfolio."""
import json
import os
from openai import OpenAI


def summarize_with_llm(ticket: str, evidence: list[dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        input=[
            {"role": "system", "content": "Use only the supplied synthetic support evidence. Do not claim actions were taken unless the evidence shows them."},
            {"role": "user", "content": f"Ticket:\n{ticket}\n\nEvidence:\n{json.dumps(evidence)[:12000]}"},
        ],
        max_output_tokens=800,
    )
    return response.output_text
