import pytest

from app.agents.graph import graph


@pytest.mark.asyncio
async def test_graph_handles_database_question():
    result = await graph.ainvoke(
        {
            "question": (
                "نام اعضایی را نمایش بده که حداقل دو کتاب امانت‌گرفته‌شده "
                "دارند که موعد بازگرداندن آن‌ها گذشته است و هنوز برگردانده "
                "نشده‌اند. برای هر عضو، نام کامل، شماره عضویت و تعداد "
                "این کتاب‌ها را نشان بده و نتایج را بر اساس تعداد کتاب‌ها "
                "از بیشترین به کمترین مرتب کن."
            ),
            "route": "general",
            "answer": "",
            "sql": None,
            "data": None,
            "sources": [],
        }
    )

    print("\nSelected route:", result["route"])
    print("Generated SQL:", result["sql"])
    print("Database results:", result["data"])
    print("Final answer:", result["answer"])

    assert result["route"] == "sql"
    assert result["sql"] is not None
    assert result["data"] is not None
    assert result["answer"]
