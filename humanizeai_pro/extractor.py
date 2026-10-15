"""
Universal Document Extractor for HumanizeAI.pro
Extracts clean, structured text from TXT, Markdown, Word (.docx), PDF, and Images.
"""

import os
from pathlib import Path
from typing import Optional


class DocumentExtractor:
    """Extracts text from multiple document formats."""

    @staticmethod
    def extract(file_path_or_text: str) -> str:
        """Extract text from file path or return string directly if not a file."""
        # If it's not a path or doesn't exist, treat as raw text
        if "\n" in file_path_or_text or not os.path.exists(file_path_or_text):
            return file_path_or_text

        path = Path(file_path_or_text)
        suffix = path.suffix.lower()

        if suffix in (".txt", ".md", ".markdown", ".rst"):
            return path.read_text(encoding="utf-8", errors="ignore")

        elif suffix == ".docx":
            return DocumentExtractor._extract_docx(path)

        elif suffix == ".pdf":
            return DocumentExtractor._extract_pdf(path)

        elif suffix in (".png", ".jpg", ".jpeg", ".webp"):
            return DocumentExtractor._extract_image(path)

        else:
            # Fallback to UTF-8 text read
            return path.read_text(encoding="utf-8", errors="ignore")

    @staticmethod
    def _extract_docx(path: Path) -> str:
        try:
            import docx
            doc = docx.Document(str(path))
            paragraphs = []
            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue
                # Add markdown header styling if style starts with Heading
                if p.style and p.style.name.startswith("Heading"):
                    try:
                        level = int(p.style.name.replace("Heading", "").strip())
                        paragraphs.append(f"{'#' * level} {text}")
                    except ValueError:
                        paragraphs.append(f"## {text}")
                else:
                    paragraphs.append(text)
            return "\n\n".join(paragraphs)
        except Exception as e:
            raise RuntimeError(f"Failed to extract DOCX: {e}")

    @staticmethod
    def _extract_pdf(path: Path) -> str:
        # Try pdfplumber first for better reading order, fallback to pypdf
        try:
            import pdfplumber
            pages_text = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt:
                        pages_text.append(txt.strip())
            if pages_text:
                return "\n\n".join(pages_text)
        except Exception:
            pass

        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            pages = []
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    pages.append(txt.strip())
            return "\n\n".join(pages)
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF: {e}")

    @staticmethod
    def _extract_image(path: Path) -> str:
        # Attempt pytesseract if available
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(str(path))
            return pytesseract.image_to_string(img)
        except Exception:
            raise RuntimeError(
                f"OCR dependencies not available for {path.name}. "
                "AI agents can inspect the image directly using vision."
            )
