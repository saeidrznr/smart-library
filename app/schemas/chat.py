from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    source: str
    page: int | None = None
    section: str | None = None
    chunk_type: str | None = None
    clause_number: str | None = None
    question_number: str | None = None
    content: str | None = None


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="User's question for the library assistant",
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    sql: str | None = None
    data: list[dict] | None = None
