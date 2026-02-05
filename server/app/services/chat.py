import asyncio
from typing import List, Dict
import json
from app.services.gemini import embed_text
from app.models import Template
from sqlalchemy.orm import Session
from app.services.gemini import client
import re
from .web_search import build_template_extraction_prompt
import math
from pydantic import BaseModel
from typing import Optional


class TemplateMatchResult(BaseModel):
    best_template_id: Optional[int]
    confidence: Optional[float] = None
    reason: str
    title: Optional[str] = ""


def gemini_choose_template(user_query: str, candidates: list):
    """
    candidates = [
      {"id": 1, "title": "...", "tags": [...], "score": 0.82},
      ...
    ]
    """

    prompt = f"""
You are selecting the best legal document template.

User request:
"{user_query}"

Candidate templates:
{json.dumps(candidates, indent=2)}

Rules:
- Choose the best template ONLY if confidence ≥ 0.6
- If none are suitable, set best_template_id to null and explain why in reason
- All other fields must still be present
- title must be a non-empty string inferred from the user request
- Consider title, tags, and similarity score
- Return strict JSON only
- return title as just which legal document user is asking from user query  

Output format:
{{
  "best_template_id": number or null,
  "confidence": number,
  "reason": string,
  "title": string,
}}
"""
    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "temperature": 0,
                "response_mime_type": "application/json",
            },
        )

        return TemplateMatchResult.model_validate_json(response.text)
    except Exception as e:
        return TemplateMatchResult(
            best_template_id=None,
            confidence=None,
            reason="Template selection failed",
            title="",
        )


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def find_best_template(
    user_query: str, templates: List[Dict]
) -> TemplateMatchResult | None:

    query_embedding = await asyncio.to_thread(embed_text, user_query)

    scored = []
    for t in templates:
        if not t.embedding:
            continue

        score = cosine_similarity(query_embedding, t.embedding)
        scored.append(
            {
                "id": t.id,
                "title": t.title,
                "tags": t.tags,
                "score": round(score, 3),
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)

    print("Score", scored)

    top_candidates = scored[:3]

    result = gemini_choose_template(user_query, top_candidates)

    return result


def create_template(
    title: str,
    raw_text: str,
    analysis: dict,
    db: Session,
) -> Template:
    body = raw_text

    # Variable replacement
    for var in analysis.get("variables", []):
        key = var.get("key")
        example_val = var.get("example", "")

        if not key or not example_val or len(example_val.strip()) < 2:
            continue

        try:
            pattern = re.compile(
                rf"\b{re.escape(example_val)}\b",
                re.IGNORECASE,
            )

            body = pattern.sub(f"{{{{{key}}}}}", body)
        except re.error:
            continue

    # Optional signature line replacement
    for var in analysis.get("variables", []):
        key = var.get("key")
        example_val = var.get("example", "")

        if not key or not example_val:
            continue

        try:
            pattern = re.compile(
                rf"Name:\s*{re.escape(example_val)}",
                re.IGNORECASE,
            )
            body = pattern.sub(f"Name: {{{{{key}}}}}", body)
        except re.error:
            continue

    # Embedding
    embedding_text = " ".join(
        [
            title,
            " ".join(analysis.get("similarity_tags", [])),
        ]
    )

    embedding = embed_text(embedding_text)

    # Save template
    new_template = Template(
        title=title,
        body=body,
        variables=analysis.get("variables", []),
        tags=analysis.get("similarity_tags", []),
        embedding=embedding,
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


def prefill_variables_from_query(
    user_query: str,
    variables: list,
):
    """
    variables = [
      {"key": "...", "label": "...", "dtype": "..."}
    ]
    """

    var_spec = [
        {
            "key": v["key"],
            "label": v.get("label", ""),
            "dtype": v.get("dtype", "string"),
        }
        for v in variables
    ]

    prompt = f"""
You extract explicitly stated values from a user request.

User request:
"{user_query}"

Template variables:
{json.dumps(var_spec, indent=2)}

Rules:
- Only extract values clearly present in the user request
- Do NOT guess or infer missing values
- Numbers must be plain digits (no commas)
- If a value is not present, omit the key
- Return JSON only

Output example:
{{ "policy_number": "302786965" }}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    )

    try:
        return json.loads(response.text)
    except Exception:
        return {}


def extract_template_from_web(title: str, raw_text: str):
    prompt = build_template_extraction_prompt(title, raw_text)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "temperature": 0,
                "response_mime_type": "application/json",
            },
        )

        result = json.loads(response.text)

        return result

    except Exception as e:
        print("LLM extraction failure:", e)
        return None


async def generate_friendly_questions(variables: list[Dict]) -> Dict[str, str]:
    """
    variables = [
      {"key": "...", "label": "...", "description": "...", "dtype": "..."}
    ]

    Returns:
    {
      "policy_number": "What is the insurance policy number exactly as it appears on the policy schedule?",
      "incident_date": "On what date did the incident occur? (YYYY-MM-DD)"
    }
    """

    prompt = f"""
You are a legal drafting assistant.

Generate one clear, professional, human-friendly question for each variable below.

Rules:
- Do NOT repeat labels or variable names
- Use the description and example to add helpful context
- Write for a real person filling out a legal form
- Be specific and unambiguous
- Include format hints only when useful
- One question per variable
- Return STRICT JSON only
- Output keys must exactly match the variable keys

Variables:
{variables}

Output:
{{
    "<variable_key>": "<question>"
    "<variable_key>": "<question>"
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    )

    try:
        return json.loads(response.text)
    except Exception:
        return {}
