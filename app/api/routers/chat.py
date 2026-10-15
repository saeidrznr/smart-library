import logging

from fastapi import APIRouter, HTTPException, status

from app.agents.graph import graph
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

logger = logging.getLogger(__name__)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="سؤال نمی‌تواند خالی باشد.",
        )

    try:
        result = await graph.ainvoke(
            {
                "question": question,
                "route": "general",
                "answer": "",
                "sql": None,
                "data": None,
                "sources": [],
                "is_final": False,
                "messages": [],
                "execution_log": [],
                "tool_steps": 0,
                "sql_history": [],
                "agents_used": []
            }
        )

        answer = result.get("answer")

        if not isinstance(answer, str) or not answer.strip():
            logger.error("Chat graph returned an empty or invalid answer.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="در تولید پاسخ خطایی رخ داد.",
            )

        return ChatResponse(
            answer=answer,
            sources=result.get("sources") or [],
            sql=result.get("sql"),
            data=result.get("data"),
            agents_used=result.get("agents_used", []),
            sql_history= result.get("sql_history", []),
            execution_log = result.get("execution_log", [])

        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Unexpected error while processing chat request.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="در پردازش درخواست خطایی رخ داد. لطفاً دوباره تلاش کنید.",
        ) from None
