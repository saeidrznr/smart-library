from typing import Literal

from pydantic import BaseModel, Field

from app.agents.state import AgentState
from app.core.llm import llm


class RouteDecision(BaseModel):
    route: Literal["sql", "documents", "general"] = Field(
        description=(
            "sql for database questions, "
            "documents for library document questions, "
            "general for greetings and general questions"
        )
    )


router_llm = llm.with_structured_output(RouteDecision)


async def coordinator(state: AgentState) -> dict:
    response = await router_llm.ainvoke(
        [
            (
                "system",
                """
You are the coordinator of a library assistant.

Choose exactly one route:

- sql: Questions requiring structured database data,
  such as library members, loans, due dates, and late fees.
- documents: Questions requiring information from library
  PDFs, regulations, policies, or other library documents.
- general: Greetings, small talk, and general questions
  that do not require database queries or library documents.

Do not answer the user's question.
Only classify the question.
""",
            ),
            ("human", state["question"]),
        ]
    )

    return {"route": response.route}