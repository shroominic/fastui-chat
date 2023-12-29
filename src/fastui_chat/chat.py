from typing import Annotated, AsyncIterable

from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import PageEvent
from langchain_core.chat_history import BaseChatMessageHistory

from .components import ChatInputForm, ChatMessage
from .db import get_history, get_session
from .session import ChatSession

router = APIRouter()


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
async def chat_history(
    history: Annotated[BaseChatMessageHistory, Depends(get_history)],
) -> list[AnyComponent]:
    """
    Endpoint for showing the Chat History UI.
    """
    return [ChatMessage(msg.type, msg.content) for msg in history.messages]


@router.post("/chat/generate", response_model=FastUI, response_model_exclude_none=True)
async def chat_generate(user_msg: Annotated[str, Form(...)]) -> list[AnyComponent]:
    """
    Endpoint for showing the Chat Generate UI.
    """
    return [
        ChatMessage("human", user_msg),
        c.ServerLoad(
            path="/chat/generate/response?user_msg=" + user_msg,
            load_trigger=PageEvent(name="generate-response"),
            components=[c.Text(text="...")],
            sse=True,
        ),
        ChatInputForm(
            submit_url="/api/chat/generate",
            fire_page_event="generate-response",
        ),
    ]


@router.get("/chat/generate/response")
async def sse_ai_response(
    user_msg: str,
    session: Annotated[ChatSession, Depends(get_session)],
) -> StreamingResponse:
    return StreamingResponse(
        ai_response_generator(user_msg, session), media_type="text/event-stream"
    )


async def ai_response_generator(
    user_msg: str,
    session: ChatSession,
) -> AsyncIterable[str]:
    output, msg = "", ""
    async for chunk in session.astream(user_msg):
        if isinstance(chunk.content, list) and isinstance(chunk.content[0], dict):
            m = FastUI(root=[ChatMessage("ai", chunk.content)])
        else:
            output += (
                chunk.content
                if not isinstance(chunk.content, list)
                else chunk.content[0]
            )
            m = FastUI(root=[ChatMessage("ai", output)])
        yield f"data: {m.model_dump_json(by_alias=True, exclude_none=True)}\n\n"

    # avoid the browser reconnecting
    while True:
        import asyncio

        yield msg
        await asyncio.sleep(5)
