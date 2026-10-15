import pytest

from app.agents.sql_agent import sql_agent


@pytest.mark.asyncio
async def test_sql_agent_returns_member_data():
    result = await sql_agent(
        {
            "question": "چند عضو در کتابخانه ثبت شده‌اند؟",
            "route": "sql",
            "answer": "",
            "sql": None,
            "data": None,
            "sources": [],
        }
    )

    assert result["sql"] is not None
    assert result["data"] is not None
    assert result["answer"]
