import google.genai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import asyncio


API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
print("API key length:", len(os.getenv("GOOGLE_API_KEY", "")))
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)


class VariableSchema(BaseModel):
    key: str
    label: str
    description: Optional[str] = ""
    example: Optional[str] = ""
    required: bool = False
    dtype: Optional[str] = "string"


class ExtractionResponse(BaseModel):
    variables: List[VariableSchema] = Field(default_factory=list)
    similarity_tags: List[str] = Field(default_factory=list)


def normalize_variables(vars: list[VariableSchema]) -> list[dict]:
    return [
        {
            "key": v.key,
            "label": v.label or v.key,
            "description": v.description or "",
            "example": v.example or "",
            "required": bool(v.required),
            "dtype": v.dtype or "string",
        }
        for v in vars
    ]


def embed_text(text: str) -> list[float]:
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text[:8000],
    )
    if not response.embeddings:
        raise ValueError("No embeddings returned from Gemini")

    return response.embeddings[0].values


async def analyze_document(text: str) -> dict:
    return await asyncio.to_thread(analyze_document_sync, text)


def analyze_document_sync(text: str) -> dict:

    # Updated Prompt Snippet for gemini.py
    prompt = f"""
        System: You are a Legal Engineer.
        Task: Convert raw legal text into a reusable template.
        Rules:
        1. Identify variables that should be templated (e.g., [Company Name], [Date], [Amount]).
        2. "key" must be snake_case and consistent across similar legal documents.
        3. "label" must be human-readable.
        4. "description" must explain legal significance.
        5. "example" must be copied verbatim from the input text.
        6. Set "required" to true if the agreement would be legally incomplete without this value.
        7. Set "dtype" to one of: string, date, number, duration.
        8. Do not invent information. Only use what exists in the text.
        Text: {text}
        Respond ONLY in valid JSON that matches the following schema:
        {{
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
        """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "temperature": 0,
                "response_mime_type": "application/json",
                "response_schema": ExtractionResponse,
            },
        )

        if not response.text or not response.text.strip():
            raise ValueError("Empty response from Gemini")

        parsed = ExtractionResponse.model_validate_json(response.text)

        return {
            "variables": normalize_variables(parsed.variables),
            "similarity_tags": parsed.similarity_tags,
        }
    except ValueError as e:
        print("Validation error:", e)
        raise
    except Exception as e:
        raw = getattr(response, "text", None) if "response" in locals() else None
        print("Raw response:", repr(raw))
        raise
