from typing import Literal, TypedDict


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

    # Execution trace for debugging and demonstration
    execution_log: list[str]

    # Number of agent executions; prevents unbounded loops
    agent_steps: int

    agents_used: list[str]
    sql_history: list[str]