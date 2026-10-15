from pathlib import Path
import re

from langchain_core.documents import Document
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"


def fix_reversed_numbers(text: str) -> str:
    """Reverse two-digit numbers when extracted in reverse order."""
    return re.sub(
        r"[0-9۰-۹]{2}",
        lambda match: match.group(0)[::-1],
        text,
    )


def load_documents() -> list[Document]:
    """Load text from all PDF files in the documents directory."""
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(
            f"Documents directory not found: {DOCUMENTS_DIR}"
        )

    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    documents: list[Document] = []

    for pdf_path in pdf_files:
        reader = PdfReader(str(pdf_path))

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if not text or not text.strip():
                continue

            text = fix_reversed_numbers(text.strip())

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_number,
                    },
                )
            )

    if not documents:
        raise ValueError(
            "No extractable text found in the PDF documents."
        )

    return documents