import pytest
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

from app.core.llm import llm


@pytest.mark.asyncio
async def test_gemini_connection():
    response = await llm.ainvoke(
        [HumanMessage(content="Reply with exactly: OK")]
    )

    assert response.content