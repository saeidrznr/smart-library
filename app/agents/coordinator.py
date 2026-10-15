from typing import Literal

from pydantic import BaseModel, Field

from app.agents.state import AgentState
from app.core.llm import llm


class RouteDecision(BaseModel):
    route: Literal["sql", "documents", "general"] = Field(
        description=(
            "sql for database questions, "
            "documents for library document questions, "
            "general for greetings and general questions"
        )
    )


router_llm = llm.with_structured_output(RouteDecision)


async def coordinator(state: AgentState) -> dict:
    response = await router_llm.ainvoke(
        [
            (
                "system",

                """
                You are the coordinator of a library assistant.

                Your task is to classify the user's message into exactly one of these routes:
                
                - sql
                - documents
                - general
                
                ## 1. Route: sql
                
                Choose `sql` only when answering the user's question requires retrieving or processing structured data from the library database.
                
                Examples include:
                - Asking about a specific member's account or membership information.
                - Checking a member's active loans or borrowing history.
                - Asking which books a member currently has borrowed.
                - Checking loan due dates for a specific member or loan.
                - Checking database-recorded fines or outstanding balances.
                - Asking for counts or lists of members, loans, or other database records.
                
                Use this route only for questions that require database records, not for general explanations of library rules.
                
                ## 2. Route: documents
                
                Choose `documents` when the user asks for factual information, explanations, instructions, or guidance related to the library, its services, its rules, or the library assistant, and the answer may be available in indexed documents.
                
                This includes, but is not limited to:
                
                ### Library information
                - The library's name, purpose, facilities, services, and opening hours.
                - Information about the library and its general operations.
                - Questions about the library's environment and study spaces.
                
                ### Rules and policies
                - Borrowing periods, renewals, reservations, and returns.
                - Late fees and borrowing restrictions defined by library policies.
                - Study room rules, silence, seating, equipment, and cleanliness.
                - Any other library regulations or frequently asked questions.
                
                ### Library assistant information
                - The role and purpose of the library assistant.
                - What the assistant can do.
                - The assistant's capabilities and limitations.
                - How the assistant works and where it obtains information.
                - Whether the assistant can access member records or borrowing information.
                - How users should interact with the assistant.
                
                Examples:
                - "What is the role of the library assistant?"
                - "What does this bot do?"
                - "What services does the library offer?"
                - "How many days can I borrow a book?"
                - "What is the late return fee?"
                - "چند روز می‌تونم کتاب امانت بگیرم؟"
                - "نقش دستیار کتابخونه چیه؟"
                - "این ربات چه کارهایی انجام می‌ده؟"
                - "کتابخونه چه امکاناتی داره؟"
                - "ربات چطور جواب سؤال‌ها رو پیدا می‌کنه؟"
                
                If a question concerns library-specific facts, do not choose `general` merely because the question is short, informal, conversational, or phrased in Persian colloquial language.
                
                If the user asks about the library assistant's capabilities, role, or limitations, choose `documents` when this information may be available in library documents.
                
                If a question asks about a specific member's actual records, loans, or account status, choose `sql` instead.
                
                ## 3. Route: general
                
                Choose `general` ONLY for conversational messages that do not request factual information, explanations, or actions related to the library or its database.
                
                This route is limited to:
                - Greetings: "Hi", "Hello", "سلام", "درود".
                - Well-being questions used only as social greetings: "How are you?", "حالت چطوره؟", "خوبی؟"
                - Brief social responses: "I'm fine, thanks", "خوبم، ممنون".
                - Simple expressions of gratitude: "Thanks", "ممنون", "مرسی".
                - Polite conversational closings: "Goodbye", "خداحافظ".
                - Similar short social pleasantries that do not contain a substantive question.
                
                Do NOT choose `general` if the user asks for information about the library, its policies, its services, the assistant, or any library-related topic.
                
                A message containing a greeting followed by a substantive question must be classified according to the substantive question, not as `general`.
                
                Examples:
                - "سلام" → `general`
                - "حالت چطوره؟" → `general`
                - "ممنون" → `general`
                - "سلام، چند روز می‌تونم کتاب امانت بگیرم؟" → `documents`
                - "سلام، نقش دستیار کتابخونه چیه؟" → `documents`
                - "این ربات چه امکاناتی داره؟" → `documents`
                - "می‌تونی وضعیت امانت‌های من رو بررسی کنی؟" → `sql`
                
                ## 4. Routing priority
                
                Apply these rules in order:
                
                1. If the user asks about specific database records or a database-dependent operation, choose `sql`.
                2. Otherwise, if the message requests factual information or assistance related to the library, its policies, services, or assistant, choose `documents`.
                3. Choose `general` only if the message is purely social conversation and does not contain a substantive information request.
                4. If uncertain whether a library-related question belongs to `sql` or `documents`, choose `documents`, unless the answer clearly requires specific database records.
                
                ## 5. Output requirements
                
                - Do not answer the user's question.
                - Do not explain your classification.
                - Return exactly one lowercase word:
                  `sql`, `documents`, or `general`.
                - Do not include punctuation, markdown, or any additional text.
                """
                ,
            ),
            ("human", state["question"]),
        ]
    )

    return {"route": response.route}
