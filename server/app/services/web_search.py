import httpx
import os


def safe_truncate(text: str, max_chars: int = 3000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0]


async def search_template_on_web(query: str):

    EXA_API_KEY = os.getenv("EXA_API_KEY")
    if not EXA_API_KEY:
        raise RuntimeError("EXA_API_KEY not set")

    search_query = f"{query} legal document example"

    payload = {
        "query": search_query,
        "useAutoprompt": True,
        "numResults": 5,
        "contents": {"text": True},
    }
    try:

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.exa.ai/search",
                json=payload,
                headers={
                    "x-api-key": EXA_API_KEY,
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Web search failed: {e}")

    data = response.json()
    results = data.get("results", [])

    if not results:
        return None

    # Use the top result
    top = results[0]
    raw_text = top.get("text", "")
    title = top.get("title", query)

    return {
        "title": top.get("title", query),
        "raw_text": safe_truncate(top.get("text", "")),
    }


def build_template_extraction_prompt(title: str, raw_text: str) -> str:
    PROMPT = """
SYSTEM ROLE:
You are a Legal Template Normalizer, not a writer and not a legal advisor.

GOAL:
Convert the provided legal document into a STRICTLY GENERIC, REUSABLE LEGAL TEMPLATE
that can be safely reused across document types, jurisdictions, and parties.

DOCUMENT TYPE:
{title}

────────────────────────
HARD RULES (NON-NEGOTIABLE)
────────────────────────

1. OUTPUT MUST NOT:
   - contain the words "sample", "example", or "specimen"
   - contain square brackets [ ]
   - contain real names, addresses, dates, currencies, IDs, places, or jurisdictions as fixed values
   - assume a country, state, or legal system

2. ALL variable data MUST:
   - be replaced using double curly braces, for example: {{{{party_a_name}}}}
   - use snake_case keys only

3. DO NOT invent, improve, or modernize clauses.
   -All structural variables must appear in the body: 
   party_a_name, party_b_name, subject_matter_description, effective_date, consideration_amount, governing_jurisdiction.
   - If a value exists, replace with {{{{variable_name}}}}.
   - If missing, leave {{{{variable_name}}}} placeholder.


FORMATTING RULES:
- Maintain clear Markdown order, numbering, and headings.
- Improve readability using line breaks and whitespace only.
- Do NOT rewrite, merge, split, or reorder clauses.
- Output must resemble a professionally formatted legal document.

────────────────────────
ROLE & ENTITY NORMALIZATION
────────────────────────

- NEVER infer or assign semantic roles.
- ALWAYS normalize parties as {{{{party_a_name}}}} and {{{{party_b_name}}}}.

────────────────────────
VARIABLE EXTRACTION RULES
────────────────────────
- Extract NO MORE THAN 6 variables total.
- Keep only structurally essential variables related to context.

example:
1. party_a_name
2. party_b_name
3. subject_matter_description
4. effective_date
5. consideration_amount
6. governing_jurisdiction

────────────────────────
OUTPUT FORMAT (STRICT)
────────────────────────

Return ONLY valid JSON in the following schema.

{{
  "body": "full legal template text using double-curly-brace variables only",
  "variables": [
    {{
      "key": "string",
      "label": "string",
      "description": "string",
      "example": "string",
      "required": true,
      "dtype": "string"
    }}
  ],
  "similarity_tags": ["string"]
}}

RAW SOURCE DOCUMENT:
{raw_text}
"""

    return PROMPT.format(title=title, raw_text=raw_text)
