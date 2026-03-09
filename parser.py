import re
import fitz  # PyMuPDF


def extract_text_from_pdf(uploaded_file):
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    full_text = []
    for page in doc:
        full_text.append(page.get_text("text"))

    return "\n".join(full_text)


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s+#./-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_sections(resume_text):
    headings = [
        "summary",
        "professional summary",
        "skills",
        "technical skills",
        "experience",
        "work experience",
        "employment",
        "education",
        "projects",
        "certifications",
    ]

    lowered = resume_text.lower()
    found = [heading for heading in headings if heading in lowered]
    return found


def extract_contact_info(text):
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_match = re.search(r"(\+?\d[\d\-\s\(\)]{7,}\d)", text)

    return {
        "email_found": bool(email_match),
        "phone_found": bool(phone_match),
    }