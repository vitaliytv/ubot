"""Витягування тексту з PDF (PyMuPDF)."""

import fitz  # PyMuPDF


def extract_text_from_pdf_bytes(data: bytes) -> str:
    """Витягує текст з PDF (bytes)."""
    doc = fitz.open(stream=data, filetype="pdf")
    try:
        parts: list[str] = []
        for page in doc:
            parts.append(page.get_text())
        return "\n".join(parts).strip()
    finally:
        doc.close()
