from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.agents.state import AgentState
from app.agents.calculator import calculator
from app.core.llm import llm
from app.agents.utils import extract_text

calculator_llm = llm.bind_tools([calculator])


async def calculator_agent(state: AgentState) -> dict:
    tool_steps = state.get("tool_steps", 0) + 1
    execution_log = state.get("execution_log", [])

    try:
        messages = [
            SystemMessage(
                content="""
You are a calculator assistant for a library system.

Your task is to perform arithmetic calculations using the
calculator tool and answer the user's original question.

Rules:
- Always use the calculator tool for arithmetic.
- Never calculate results mentally or invent numerical results.
- If database results are provided, use them as the source
  of numerical values for the calculation.
- Never invent missing database values.
- If the required information is missing, explain what is missing.
- Pass only a valid mathematical expression to the calculator
  tool using its `expression` argument.
- After receiving the tool result, answer concisely in Persian.
- Do not answer unrelated questions.
"""
            ),
            HumanMessage(
                content=f"""
Original question:
{state["question"]}

Database results, if available:
{state.get("data")}

Previous answer, if available:
{state.get("answer")}
"""
            ),
        ]

        response = await calculator_llm.ainvoke(messages)
        messages.append(response)

        tool_results = []

        for tool_call in response.tool_calls:
            if tool_call["name"] != calculator.name:
                continue

            execution_log = execution_log + [
                f"calculator tool called: {tool_call['args']['expression']}"
            ]

            result = await calculator.ainvoke(tool_call["args"])

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

            tool_results.append(str(result))

        if response.tool_calls:
            final_response = await llm.ainvoke(messages)
            answer = final_response.content
        else:
            answer = response.content

        answer = extract_text(answer)

        return {
            "answer": answer,
            "sql": state.get("sql"),
            "data": state.get("data"),
            "sources": state.get("sources", []),
            "tool_steps": tool_steps,
            "execution_log": execution_log + [
                "calculator_agent executed"
            ],
            "agents_used": state.get("agents_used", []) + ["calculator_agent"],
        }

    except Exception:
        return {
            "answer": (
                "در انجام محاسبه خطایی رخ داد. "
                "لطفاً سؤال خود را بررسی کنید."
            ),
            "sql": state.get("sql"),
            "data": state.get("data"),
            "sources": state.get("sources", []),
            "tool_steps": tool_steps,
            "execution_log": execution_log + [
                "calculator_agent failed"
            ],
            "agents_used": state.get("agents_used", []) + ["calculator_agent"],
        }
