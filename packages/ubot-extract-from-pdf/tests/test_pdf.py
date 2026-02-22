"""Тести експорту тексту з PDF."""

import pytest

from ubot_extract_from_pdf.pdf import extract_text_from_pdf_bytes


def test_extract_text_from_pdf_bytes_invalid() -> None:
    with pytest.raises(Exception):
        extract_text_from_pdf_bytes(b"not a pdf")


def test_extract_text_from_pdf_bytes_minimal() -> None:
    minimal_pdf = (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Hello) Tj\nET\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n298\n%%EOF"
    )
    text = extract_text_from_pdf_bytes(minimal_pdf)
    assert "Hello" in text or "hello" in text.lower()
