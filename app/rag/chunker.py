import re
from collections import defaultdict

from langchain_core.documents import Document

ARTICLE_PATTERN = re.compile(
    r"(?m)^[ \t]*(ماده[ \t]*[۰-۹0-9]+[^\n]*)"
)

CLAUSE_PATTERN = re.compile(
    r"(?m)^[ \t]*([۰-۹0-9]+)[ \t]*[.)ـ][ \t]*"
)

QUESTION_PATTERN = re.compile(
    r"(?m)^[ \t]*س[ \t]*و?[ \t]*[اأإآ]?[ \t]*ل"
    r"[ \t]*([۰-۹0-9]+)[ \t]*[:：]"
)

SECTION_PATTERN = re.compile(
    r"(?m)^[ \t]*(بخش[ \t]+[^\n]+)"
)


def normalize_text(text: str) -> str:
    """Normalize Persian text while preserving line boundaries."""
    text = text.replace("---", "").replace("ؤ", "و").replace("ئ", "ی").replace("ي", "ی").replace("ك", "ک")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def group_documents(
        documents: list[Document],
) -> dict[str, list[Document]]:
    """Group pages belonging to the same source PDF."""
    grouped = defaultdict(list)

    for document in documents:
        source = document.metadata.get("source", "unknown")
        grouped[source].append(document)

    for pages in grouped.values():
        pages.sort(
            key=lambda doc: int(doc.metadata.get("page", 0))
        )

    return dict(grouped)


def merge_pages(pages: list[Document]) -> str:
    """Merge PDF pages before splitting to preserve cross-page content."""
    return normalize_text(
        "\n\n".join(
            page.page_content
            for page in pages
            if page.page_content.strip()
        )
    )


def split_articles(text: str) -> list[tuple[str, str]]:
    """Return article title and article content."""
    matches = list(ARTICLE_PATTERN.finditer(text))

    if not matches:
        return []

    articles = []

    for index, match in enumerate(matches):
        start = match.start()
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        title = match.group(1).strip()
        content = text[start + len(match.group(1)):end].strip()

        articles.append((title, content))

    return articles


def chunk_article_document(
        text: str,
        source: str,
) -> list[Document]:
    """Create one chunk per numbered clause, prefixed by its article title."""
    chunks = []

    for article_title, article_text in split_articles(text):

        matches = list(CLAUSE_PATTERN.finditer(article_text))

        # If an article has no numbered clauses, keep it as one chunk.
        if not matches:
            if article_text:
                chunks.append(
                    Document(
                        page_content=f"{article_title}\n{article_text}",
                        metadata={
                            "source": source,
                            "section": article_title,
                            "chunk_type": "article",
                        },
                    )
                )
            else:
                chunks.append(
                    Document(
                        page_content=article_title,
                        metadata={
                            "source": source,
                            "section": article_title,
                            "chunk_type": "article",
                        },
                    )
                )
            continue

        # Preserve any text between the article title and first clause.
        preamble = article_text[:matches[0].start()].strip()
        if preamble:
            chunks.append(
                Document(
                    page_content=f"{article_title}\n{preamble}",
                    metadata={
                        "source": source,
                        "section": article_title,
                        "chunk_type": "article_intro",
                    },
                )
            )

        for index, match in enumerate(matches):
            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(article_text)
            )

            clause_text = article_text[match.start():end].strip()
            clause_number = match.group(1)

            content = f"{article_title}\n{clause_text}"

            chunks.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": source,
                        "section": article_title,
                        "clause_number": clause_number,
                        "chunk_type": "article_clause",
                    },
                )
            )

    return chunks


def chunk_faq_document(
        text: str,
        source: str,
) -> list[Document]:
    """Create one chunk per question and its complete answer."""
    question_matches = list(QUESTION_PATTERN.finditer(text))
    section_matches = list(SECTION_PATTERN.finditer(text))

    chunks = []

    for index, match in enumerate(question_matches):
        start = match.start()
        end = (
            question_matches[index + 1].start()
            if index + 1 < len(question_matches)
            else len(text)
        )

        question_number = match.group(1)
        question_text = text[match.end():].split("\n", 1)[0].strip()
        answer_text = text[match.end():end].strip()

        # Include the nearest preceding section heading, if present.
        section_title = None
        for section_match in reversed(section_matches):
            if section_match.start() < start:
                section_title = section_match.group(1).strip()
                break

        parts = []
        if section_title:
            parts.append(section_title)

        if answer_text:
            parts.append(answer_text)

        chunks.append(
            Document(
                page_content="\n".join(parts),
                metadata={
                    "source": source,
                    "section": section_title or "پرسش و پاسخ",
                    "question_number": question_number,
                    "chunk_type": "faq",
                },
            )
        )

    return chunks


def chunk_library_intro_document(
        text: str,
        source: str,
) -> list[Document]:
    """Create one chunk per numbered subsection in the library introduction."""
    chunks = []

    section_matches = list(SECTION_PATTERN.finditer(text))

    # Find numbered headings such as "۱. معرفی کلی"
    heading_pattern = re.compile(
        r"(?m)^[ \t]*([۰-۹0-9]+)[ \t]*[.)ـ][ \t]*(.+?)\s*$"
    )
    heading_matches = list(heading_pattern.finditer(text))

    for index, match in enumerate(heading_matches):
        start = match.start()
        end = (
            heading_matches[index + 1].start()
            if index + 1 < len(heading_matches)
            else len(text)
        )

        heading_number = match.group(1)
        heading_title = match.group(2).strip()
        content = text[start:end].strip()

        section_title = "معرفی کتابخانه و دستیار هوشمند"

        for section_match in reversed(section_matches):
            if section_match.start() < start:
                section_title = section_match.group(1).strip()
                break

        chunks.append(
            Document(
                page_content=f"{section_title}\n{content}",
                metadata={
                    "source": source,
                    "section": section_title,
                    "heading": heading_title,
                    "clause_number": heading_number,
                    "chunk_type": "library_intro",
                },
            )
        )

    return chunks


def chunk_documents(
        documents: list[Document],
) -> list[Document]:
    """Route each PDF to its appropriate chunking strategy."""
    grouped = group_documents(documents)
    all_chunks = []

    for source, pages in grouped.items():
        text = merge_pages(pages)
        filename = source.replace("\\", "/").split("/")[-1]

        if "پرسش و پاسخ" in filename:
            chunks = chunk_faq_document(text, source)
        elif "معرفی کتابخانه و دستیار هوشمند" in filename:
            chunks = chunk_library_intro_document(text, source)
        elif (
                "قوانین امانت" in filename
                or "قوانین فضای مطالعه" in filename
        ):
            chunks = chunk_article_document(text, source)

        else:
            # Leave unsupported documents untouched as one chunk per source.
            chunks = [
                Document(
                    page_content=text,
                    metadata={
                        "source": source,
                        "chunk_type": "document",
                    },
                )
            ]

        all_chunks.extend(chunks)

    return all_chunks
