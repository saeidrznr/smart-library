from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceReference(BaseModel):
    source: str
    page: int | None = None
    section: str | None = None
    chunk_type: str | None = None
    clause_number: str | None = None
    question_number: str | None = None
    content: str | None = None


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(
        min_length=1,
        max_length=2000,
        description="User's question for the library assistant",
        examples=[
            "اسم پنج نفر از اعضای کتابخونه رو بهم بگو"
        ]
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    sql: str | None = None
    data: list[dict] | None = None
    agents_used: list[str] = Field(default_factory=list)
    sql_history: list[str] = Field(default_factory=list)
    execution_log: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer": "پنج نفر از اعضای کتابخانه عبارتند از:\n۱. علی رضایی\n۲. سارا محمدی\n۳. محمد کریمی\n۴. فاطمه احمدی\n۵. رضا حسینی",
                "sources": [],
                "sql": "SELECT full_name AS member_name FROM members LIMIT 5",
                "data": [
                    {
                        "member_name": "علی رضایی"
                    },
                    {
                        "member_name": "سارا محمدی"
                    },
                    {
                        "member_name": "محمد کریمی"
                    },
                    {
                        "member_name": "فاطمه احمدی"
                    },
                    {
                        "member_name": "رضا حسینی"
                    }
                ],
                "agents_used": [
                    "sql_agent"
                ],
                "sql_history": [
                    "SELECT full_name AS member_name FROM members LIMIT 5"
                ],
                "execution_log": [
                    "sql_agent executed"
                ]
            }
        }
    )
