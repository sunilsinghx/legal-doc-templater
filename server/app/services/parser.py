import pdfplumber
from docx import Document
import io


async def extract_text_from_file(file):
    content = await file.read()
    extension = file.filename.split(".")[-1].lower()

    if extension == "pdf":
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif extension == "docx":
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError("Unsupported file type. Please upload PDF or DOCX.")
