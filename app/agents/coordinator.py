from typing import Literal

from pydantic import BaseModel, Field

from app.agents.state import AgentState
from app.core.llm import llm


class RouteDecision(BaseModel):
    is_final: bool = Field(
        description=(
            "True if the original question has been fully answered; "
            "otherwise False."
        )
    )

    route: Literal[
        "sql",
        "documents",
        "calculator",
        "general",
    ] = Field(
        description="The next agent to execute if is_final is False."
    )


router_llm = llm.with_structured_output(RouteDecision)


async def coordinator(state: AgentState) -> dict:
    question = state["question"]
    answer = state.get("answer") or ""
    data = state.get("data")
    sources = state.get("sources", [])
    execution_log = state.get("execution_log", [])

    # If an agent has already produced a result, decide whether
    # another step is required instead of blindly repeating it.
    decision = await router_llm.ainvoke(
        [
            (
                "system",
                """
                You are the coordinator of a library assistant built with LangGraph.

                Your job is to decide whether the user's original question is fully answered or which agent must execute next.

                Available agents:
                - sql: retrieve factual data from the library database.
                - documents: retrieve facts from library policies and documents.
                - calculator: perform arithmetic using the calculator tool.
                - general: handle greetings and general questions.

                ## Decision rules

                1. Set `is_final=True` only when every required part of the original question has been answered using available evidence.

                2. If the question requires database information that has not been retrieved, choose `sql`.

                3. If the question requires information from library policies or documents that has not been retrieved, choose `documents`.

                4. If the question requires arithmetic, percentages, ratios, averages, differences, totals derived from multiple values, or other numerical calculations that have not yet been performed, choose `calculator`.

                5. **Mandatory calculation rule:** If SQL results are available but the original question still requires a calculation, choose `calculator`. Do not finalize merely because the SQL query succeeded or returned enough numbers to calculate the answer mentally.

                6. Before selecting `calculator`, check whether the required input values are already present in the execution history or agent results. If they are available, route directly to `calculator` without repeating SQL.

                7. Do not consider a calculation completed unless the execution history or tool results provide evidence that the calculator was actually called and its result is available.

                8. For multi-part questions, ensure every required part is completed. For example, a question asking for the number of open loans and the percentage of all loans that are open requires SQL to retrieve the counts and calculator to compute the percentage.

                9. Review the original question, execution history, and existing results before choosing the next step. Reuse valid results and avoid unnecessary repeated calls.

                10. Never invent database facts, calculation results, tool executions, or missing evidence.

                11. Set `is_final=True` only when all required retrieval and calculation steps are complete. If a required step cannot be completed, finalize with an explanation of what remains unanswered rather than claiming success.

                12. When `is_final=False`, select the most appropriate next agent in `route`. When `is_final=True`, the route is ignored.

                Return only the structured decision:
                - `is_final`: whether the original question has been sufficiently answered.
                - `route`: the next agent to execute, ignored when `is_final=True`.
                """
                ,
            ),
            (
                "human",
                f"""
Original question:
{question}

Current answer:
{answer}

SQL result:
{data}

Sources:
{sources}

Execution history:
{execution_log}
""",
            ),
        ]
    )

    return {
        "is_final": decision.is_final,
        "route": decision.route,
    }



