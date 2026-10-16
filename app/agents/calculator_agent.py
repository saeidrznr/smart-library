from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.agents.state import AgentState
from app.agents.calculator import calculator
from app.core.llm import llm
from app.agents.utils import extract_text

calculator_llm = llm.bind_tools([calculator])


async def calculator_agent(state: AgentState) -> dict:
    tool_steps = state.get("tool_steps", 0) + 1
    execution_log = list(state.get("execution_log", []))
    agents_used = list(state.get("agents_used", []))

    base_result = {
        "sql": state.get("sql"),
        "data": state.get("data"),
        "sources": state.get("sources", []),
        "tool_steps": tool_steps,
    }

    try:
        data = state.get("data")

        if not data:
            return {
                **base_result,
                "answer": "اطلاعات کافی برای انجام محاسبه در دسترس نیست.",
                "execution_log": execution_log
                + ["calculator_agent skipped: missing database data"],
                "agents_used": agents_used + ["calculator_agent"],
            }

        messages = [
            SystemMessage(
                content="""
شما عامل محاسباتی یک دستیار کتابخانه هستید.

وظیفه شما انجام محاسبات موردنیاز سؤال کاربر با استفاده از ابزار
ماشین‌حساب است.

قوانین الزامی:
۱. برای هر محاسبه حتماً ابزار calculator را فراخوانی کنید.
۲. هرگز محاسبه را ذهنی انجام ندهید و نتیجه را حدس نزنید.
۳. فقط از مقادیر موجود در نتایج پایگاه داده استفاده کنید.
۴. نام هر فیلد را دقیقاً بررسی کنید تا مقدار مربوط به هر کمیت
   را با مقدار کمیت دیگری اشتباه نگیرید.
۵. اگر داده‌های لازم موجود نیستند یا ارتباط مقادیر با سؤال
   مشخص نیست، ابزار را فراخوانی نکنید و کمبود اطلاعات را اعلام کنید.
۶. فقط عبارت ریاضی معتبر را به آرگومان expression ابزار بدهید.
۷. پس از دریافت نتیجه ابزار، پاسخ نهایی را به فارسی بنویسید.
۸. نتیجه محاسبه باید مستقیماً از خروجی ابزار گرفته شود.
۹. هیچ مقدار یا نتیجه‌ای را اختراع نکنید.
"""
            ),
            HumanMessage(
                content=f"""
سؤال اصلی کاربر:
{state["question"]}

داده‌های پایگاه داده:
{data}

کوئری اجراشده:
{state.get("sql")}

عبارت ریاضی موردنیاز را مشخص کنید و فقط با ابزار calculator
آن را محاسبه کنید.
"""
            ),
        ]

        response = await calculator_llm.ainvoke(messages)

        calculator_calls = [
            call for call in response.tool_calls
            if call["name"] == calculator.name
        ]

        if not calculator_calls:
            return {
                **base_result,
                "answer": (
                    "محاسبه انجام نشد؛ ابزار ماشین‌حساب "
                    "فراخوانی نشده است."
                ),
                "execution_log": execution_log
                + ["calculator tool was not called"],
                "agents_used": agents_used + ["calculator_agent"],
            }

        tool_results = []

        for call in calculator_calls:
            expression = call["args"].get("expression")

            if not expression:
                continue

            execution_log.append(
                f"calculator tool called: {expression}"
            )

            result = await calculator.ainvoke(
                {"expression": expression}
            )

            tool_results.append(str(result))

            messages.extend([
                response,
                ToolMessage(
                    content=str(result),
                    tool_call_id=call["id"],
                ),
            ])

        if not tool_results:
            return {
                **base_result,
                "answer": "ابزار ماشین‌حساب نتیجه‌ای ارائه نکرد.",
                "execution_log": execution_log
                + ["calculator returned no result"],
                "agents_used": agents_used + ["calculator_agent"],
            }

        messages.append(
            HumanMessage(
                content=(
                    "فقط بر اساس نتیجه واقعی ابزار زیر، پاسخ نهایی را "
                    "به فارسی بنویس. محاسبه مجدد انجام نده و عدد جدید "
                    "تولید نکن.\n"
                    f"نتیجه ابزار: {tool_results}"
                )
            )
        )

        final_response = await llm.ainvoke(messages)

        return {
            **base_result,
            "answer": extract_text(final_response.content),
            "execution_log": execution_log
            + ["calculator_agent executed"],
            "agents_used": agents_used + ["calculator_agent"],
        }

    except Exception as exc:
        return {
            **base_result,
            "answer": "در انجام محاسبه خطایی رخ داد.",
            "execution_log": execution_log
            + [f"calculator_agent failed: {type(exc).__name__}"],
            "agents_used": agents_used + ["calculator_agent"],
        }
