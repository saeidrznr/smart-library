from langgraph.graph import END, START, StateGraph

from app.agents.coordinator import coordinator
from app.agents.state import AgentState
from app.agents.sql_agent import sql_agent
from app.agents.document_agent import document_agent
from app.agents.calculator_agent import calculator_agent


async def general_agent(state: AgentState) -> dict:
    return {
        "answer": (
            "سلام! من دستیار هوشمند کتابخانه هستم. "
            "می‌توانم درباره اطلاعات اعضا، امانت‌ها و اسناد "
            "کتابخانه به شما کمک کنم."
        ),
        "sql": None,
        "data": None,
        "sources": [],
    }


MAX_STEPS = 3


def route_question(state: AgentState) -> str:
    if state.get("is_final", False):
        return END

    if state.get("tool_steps", 0) >= MAX_STEPS:
        return "limit"

    return state["route"]



async def step_limit_agent(state: AgentState) -> dict:
    answer = state.get("answer")
    tool_steps = state.get("tool_steps", 0)
    execution_log = state.get("execution_log", [])

    if tool_steps >= MAX_STEPS:
        message = (
            "برای تکمیل درخواست، محدودیت تعداد مراحل اجرا "
            "رسید. لطفاً درخواست را ساده‌تر یا به چند بخش "
            "تقسیم کنید."
        )
        log_entry = "step_limit_reached"

    elif not isinstance(answer, str) or not answer.strip():
        message = (
            "متأسفم، نتوانستم پاسخ معتبری برای این سؤال تولید کنم. "
            "لطفاً سؤال خود را درباره خدمات و اطلاعات کتابخانه مطرح کنید."
        )
        log_entry = "empty_answer_fallback"

    else:
        message = answer
        log_entry = "step_limit_agent_executed"

    return {
        "answer": message,
        "is_final": True,
        "execution_log": execution_log + [log_entry],
    }


builder = StateGraph(AgentState)

builder.add_node("coordinator", coordinator)
builder.add_node("sql_agent", sql_agent)
builder.add_node("document_agent", document_agent)
builder.add_node("calculator_agent", calculator_agent)
builder.add_node("general_agent", general_agent)
builder.add_node("step_limit_agent", step_limit_agent)

builder.add_edge(START, "coordinator")

builder.add_conditional_edges(
    "coordinator",
    route_question,
    {
        END: END,
        "sql": "sql_agent",
        "documents": "document_agent",
        "calculator": "calculator_agent",
        "general": "general_agent",
        "limit": "step_limit_agent",
    },
)

builder.add_edge("step_limit_agent", END)

# After each agent finishes, return to the coordinator.
builder.add_edge("sql_agent", "coordinator")
builder.add_edge("document_agent", "coordinator")
builder.add_edge("calculator_agent", "coordinator")
builder.add_edge("general_agent", "coordinator")

graph = builder.compile()
