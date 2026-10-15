from fastapi import APIRouter

from app.agents.graph import graph
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await graph.ainvoke(
        {
            "question": request.question,
            "route": "general",
            "answer": "",
            "sql": None,
            "data": None,
            "sources": [],
        }
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        sql=result.get("sql"),
        data=result.get("data"),
    )
