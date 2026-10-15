from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    question: str

    route: Literal[
        "sql",
        "documents",
        "calculator",
        "general",
    ]

    answer: str
    sql: str | None
    data: list[dict] | None
    sources: list[str]

    # Whether the coordinator should end the workflow
    is_final: bool

    # Messages exchanged between the agent and tools
    messages: Annotated[list[BaseMessage], add_messages]

    # Execution trace for debugging and demonstration
    execution_log: list[str]

    # Number of agent executions; prevents unbounded loops
    tool_steps: int

    agents_used: list[str]
    sql_history: list[str]