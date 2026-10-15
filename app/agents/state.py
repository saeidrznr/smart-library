from typing import Literal, TypedDict

class AgentState(TypedDict):
    question: str
    route: Literal["sql", "documents", "general"]
    answer: str
    sql: str | None
    data: list[dict] | None
    sources: list[str]