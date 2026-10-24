import pytest
from dotenv import load_dotenv

load_dotenv()

import app.agents.coordinator as coordinator_module
from app.agents.coordinator import RouteDecision
from app.agents.graph import graph


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("question", "expected_route"),
    [
        ("چند عضو در کتابخانه داریم؟", "sql"),
        ("قوانین تمدید امانت در اسناد چیست؟", "documents"),
        ("سلام، حالت چطوره؟", "general"),
    ],
)
async def test_coordinator_routes_correctly(
        question: str,
        expected_route: str,
        monkeypatch,
):
    class FakeRouter:
        async def ainvoke(self, messages):
            return RouteDecision(route=expected_route, is_final=False)

    monkeypatch.setattr(
        coordinator_module,
        "router_llm",
        FakeRouter(),
    )

    result = await graph.ainvoke(
        {
            "question": question,
            "route": "general",
            "answer": "",
            "sql": None,
            "data": None,
            "sources": [],
        }
    )

    assert result["route"] == expected_route
    assert result["answer"]
