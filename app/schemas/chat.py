from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="User's question for the library assistant",
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    sql: str | None = None
    data: list[dict] | None = None
