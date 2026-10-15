from langgraph.graph import END, START, StateGraph

from app.agents.coordinator import coordinator
from app.agents.state import AgentState


async def sql_agent_placeholder(state: AgentState) -> dict:
    return {
        "answer": "SQL agent is not implemented yet.",
    }


async def document_agent_placeholder(state: AgentState) -> dict:
    return {
        "answer": "Document RAG agent is not implemented yet.",
    }


async def general_agent(state: AgentState) -> dict:
    return {
        "answer": (
            "سلام! من دستیار هوشمند کتابخانه هستم. "
            "می‌توانم درباره اطلاعات اعضا، امانت‌ها و اسناد "
            "کتابخانه به شما کمک کنم."
        ),
    }


def route_question(state: AgentState) -> str:
    return state["route"]


builder = StateGraph(AgentState)

builder.add_node("coordinator", coordinator)
builder.add_node("sql_agent", sql_agent_placeholder)
builder.add_node("document_agent", document_agent_placeholder)
builder.add_node("general_agent", general_agent)

builder.add_edge(START, "coordinator")

builder.add_conditional_edges(
    "coordinator",
    route_question,
    {
        "sql": "sql_agent",
        "documents": "document_agent",
        "general": "general_agent",
    },
)

builder.add_edge("sql_agent", END)
builder.add_edge("document_agent", END)
builder.add_edge("general_agent", END)

graph = builder.compile()