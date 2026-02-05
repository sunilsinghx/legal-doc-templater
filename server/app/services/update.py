from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Template
import re

SIGNATURE_KEYS = {
    "disclosing_party_name": "{{disclosing_party_name}}",
    "receiving_party_name": "{{receiving_party_name}}",
}


def update_existing_templates():
    db: Session = SessionLocal()
    updated_templates = 0
    total_replacements = 0

    try:
        templates = db.query(Template).all()

        for tpl in templates:
            if not tpl.body or not tpl.variables:
                continue

            if not isinstance(tpl.variables, list):
                continue

            original_body = tpl.body
            body = original_body
            replacements_in_template = 0

            for var in tpl.variables:
                key = var.get("key")
                example = var.get("example", "")

                if key in SIGNATURE_KEYS and example:
                    pattern = rf"Name:\s*{re.escape(example)}\b"
                    body, count = re.subn(
                        pattern,
                        f"Name: {SIGNATURE_KEYS[key]}",
                        body,
                        flags=re.IGNORECASE,
                    )
                    replacements_in_template += count

            if body != original_body:
                tpl.body = body
                db.add(tpl)
                updated_templates += 1
                total_replacements += replacements_in_template

        db.commit()

        print(
            f"Template update complete: "
            f"{updated_templates} templates updated, "
            f"{total_replacements} replacements made."
        )

    except Exception as e:
        db.rollback()
        print("Template update failed:", e)
        raise

    finally:
        db.close()
