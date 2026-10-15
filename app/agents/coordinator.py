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
    tool_steps = state.get("tool_steps", 0)

    # If an agent has already produced a result, decide whether
    # another step is required instead of blindly repeating it.
    decision = await router_llm.ainvoke(
        [
            (
                "system",

                """
                You are the coordinator of a library assistant.
                
                Choose the next agent to execute, or decide that the task is complete.
                
                Available agents:
                - sql: retrieve data from the library database.
                - documents: retrieve facts from library policies and documents.
                - calculator: perform calculations using the calculator tool.
                - general: handle greetings and casual conversation.
                
                ## Decision rules
                
                1. If the original question has been fully answered, set
                   is_final=True.
                
                2. Otherwise, choose the agent that can answer the most important
                   unanswered part of the question.
                
                3. Use SQL for database facts, documents for library policies,
                   and calculator for arithmetic.
                
                4. For multi-part questions, process each required part separately.
                   For example, a question asking for an overdue-loan percentage
                   and the applicable fine may require SQL, documents, and calculator.
                
                5. Review the execution history and existing results before choosing
                   an agent. Reuse valid results and do not repeat completed work
                   unless the existing result is insufficient.
                
                6. If SQL data is available and only a calculation remains, choose
                   calculator, not SQL.
                
                7. Never invent missing facts or claim that a task was completed
                   without supporting results.
                
                8. If no useful step remains, finalize the response and clearly
                   explain any unanswered part.
                
                Return only the structured decision:
                - is_final: whether the original question is sufficiently answered.
                - route: the next agent, ignored when is_final=True.
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

Steps executed:
{tool_steps}
""",
            ),
        ]
    )

    return {
        "is_final": decision.is_final,
        "route": decision.route,
    }
