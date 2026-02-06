import os
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional

from .database import engine, SessionLocal, Base, check_db
from .models import Template

from .services.web_search import search_template_on_web
from .services.parser import extract_text_from_file
from .services.gemini import analyze_document
from .services.chat import (
    extract_template_from_web,
    generate_friendly_questions,
    find_best_template,
    prefill_variables_from_query,
    create_template,
)
from .seed_templates import seed_templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Legal Doc AI")


cors_origins = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in cors_origins.split(",") if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

    check_db()
    db = SessionLocal()
    try:
        # seed_templates(db)
        pass
    finally:
        db.close()


class DraftRequest(BaseModel):
    query: str


class SubmitAnswersRequest(BaseModel):
    template_id: int
    answers: Dict[str, str]
    prefilled: Optional[Dict[str, str]] = None


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...), db: Session = Depends(get_db)):

    # 1 Extract Text
    try:
        raw_text = await extract_text_from_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to extract text from file")

    # 2 AI Analysis
    try:
        analysis = await analyze_document(raw_text)
    except Exception:
        raise HTTPException(status_code=500, detail="Document analysis failed")

    new_template = create_template(
        title=file.filename, raw_text=raw_text, analysis=analysis, db=db
    )

    return {
        "status": "success",
        "template_id": new_template.id,
        "detected_variables": len(analysis.get("variables", [])),
    }


@app.get("/health")
async def health():
    return {"message": "Working..."}


@app.post("/start-draft")
async def start_draft(request: DraftRequest, db: Session = Depends(get_db)):

    query = request.query
    templates = db.query(Template).all()

    try:
        result = await find_best_template(query, templates)
    except Exception as e:
        print("error",e)
        raise HTTPException(500, "Template matching failed")

    is_new_template = False

    if result.best_template_id is None or result.confidence < 0.6:
        web_result = await search_template_on_web(result.title)
        if not web_result:
            raise HTTPException(404, "No template found on web")

        extracted = extract_template_from_web(
            web_result["title"], web_result["raw_text"]
        )

        if not extracted:
            raise HTTPException(500, "LLM failed to extract template")

        new_template = create_template(
            title=result.title,
            raw_text=extracted["body"],
            analysis={
                "variables": extracted["variables"],
                "similarity_tags": extracted.get("similarity_tags", []),
            },
            db=db,
        )
        is_new_template = True
        template = db.query(Template).get(new_template.id)
    else:
        template = db.query(Template).get(result.best_template_id)

    if not template:
        raise HTTPException(404, "Template not found")

    prefilled_answers = prefill_variables_from_query(
        user_query=query,
        variables=template.variables,
    )

    missing_vars = []

    for v in template.variables:
        if v["key"] not in prefilled_answers:
            missing_vars.append(v)

    confidence = None if is_new_template else result.confidence
    reason = None if is_new_template else result.reason

    if missing_vars:
        questions = await generate_friendly_questions(missing_vars)

        return {
            "template_id": template.id,
            "template_title": template.title,
            "prefilled": prefilled_answers,
            "questions": questions,
            "missing_keys": list(questions.keys()),
        }

    return {
        "template_id": template.id,
        "confidence": confidence,
        "reason": reason,
        "template_title": template.title,
    }


@app.post("/finish-draft")
async def submit_answers(
    payload: SubmitAnswersRequest,
    db: Session = Depends(get_db),
):

    template = db.query(Template).get(payload.template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    final_answers = {
        **(payload.prefilled or {}),
        **payload.answers,
    }

    for var in template.variables:
        key = var["key"]

        if var.get("required") and key not in final_answers:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {var.get('label', key)}",
            )

    # Render markdown
    final_doc = template.body
    for key, value in final_answers.items():
        final_doc = final_doc.replace(f"{{{{{key}}}}}", value)

    return {
        "status": "success",
        "template_id": template.id,
        "output": final_doc,
        "filled_variables": final_answers,
    }
