from typing import Annotated, AsyncIterable

from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import PageEvent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory

from .components import ChatInputForm, ChatMessage
from .session import ChatSession, create_basic_chat_handler

router = APIRouter()

history = ChatMessageHistory()

session = ChatSession(
    chat_handler=create_basic_chat_handler(ChatOpenAI()),
    history=history,
)


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
async def chat_ui() -> list[AnyComponent]:
    """
    Main endpoint for showing the Chat UI and handling user input.
    """
    return [
        c.Page(
            components=[
                c.ServerLoad(
                    path="/chat/history",
                    load_trigger=PageEvent(name="chat-load"),
                    components=[],
                ),
                ChatInputForm(
                    submit_url="/api/chat/generate",
                    fire_page_event="chat-load",
                ),
            ],
        )
    ]


@router.get("/chat/history", response_model=FastUI, response_model_exclude_none=True)
async def chat_history() -> list[AnyComponent]:
    """
    Endpoint for showing the Chat History UI.
    """
    return [*(ChatMessage(msg.type, msg.content) for msg in history.messages)]


@router.post("/chat/generate", response_model=FastUI, response_model_exclude_none=True)
async def chat_generate(user_msg: Annotated[str, Form(...)]) -> list[AnyComponent]:
    """
    Endpoint for showing the Chat Generate UI.
    """
    return [
        ChatMessage("human", user_msg),
        c.ServerLoad(
            path="/chat/generate/sse-response?user_msg=" + user_msg,
            load_trigger=PageEvent(name="generate-response"),
            components=[c.Text(text="...")],
            sse=True,
        ),
        ChatInputForm(
            submit_url="/api/chat/generate",
            fire_page_event="generate-response",
        ),
    ]


@router.get("/chat/generate/sse-response")
async def sse_ai_response(user_msg: str) -> StreamingResponse:
    return StreamingResponse(
        ai_response_generator(user_msg), media_type="text/event-stream"
    )


async def ai_response_generator(user_msg: str) -> AsyncIterable[str]:
    output, msg = "", ""
    async for chunk in session.astream(user_msg):
        output += chunk.content
        m = FastUI(root=[ChatMessage("ai", output)])
        yield f"data: {m.model_dump_json(by_alias=True, exclude_none=True)}\n\n"

    # avoid the browser reconnecting
    while True:
        import asyncio

        yield msg
        await asyncio.sleep(5)
