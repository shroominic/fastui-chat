from asyncio import sleep as asleep
from typing import Annotated, AsyncIterable, Callable
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, Path
from fastapi.responses import StreamingResponse
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import GoToEvent, PageEvent
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from .components import ChatInputForm, ChatMessage
from .history_factories import create_get_chat_session_dependency
from .session import ChatSession


async def stream_response_generator(
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

    if output:
        # todo img compatability
        session.history.add_ai_message(output)

    # avoid the browser reconnecting
    while True:
        yield msg
        await asleep(5)


class ChatAPIRouter(APIRouter):
    def __init__(
        self,
        history_getter: Callable[..., BaseChatMessageHistory],
        chat_handler: Runnable[HumanMessage, AIMessage],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.get_chat_session = create_get_chat_session_dependency(
            history_getter, chat_handler
        )

        @self.get("/", response_model=FastUI, response_model_exclude_none=True)
        async def index() -> list[AnyComponent]:
            return [
                c.Page(
                    components=[
                        c.Text(text="Welcome to the Chat UI!"),
                        c.Button(
                            text="New Chat",
                            on_click=GoToEvent(url=f"/{uuid4().hex}"),
                            class_name="btn btn-primary col-lg-2 mx-3 my-2",
                        ),
                    ],
                    class_name="vstack justify-content-center align-items-center",
                )
            ]

        @self.get(
            "/{session_id}", response_model=FastUI, response_model_exclude_none=True
        )
        async def chat_ui(
            session_id: Annotated[str, Path(title="The ChatHistory SessionID.")],
        ) -> list[AnyComponent]:
            """
            Main endpoint for showing the Chat UI and handling user input.
            """
            return [
                c.Page(
                    components=[
                        c.ServerLoad(
                            path="/chat/history/" + session_id,
                            load_trigger=PageEvent(name="chat-load"),
                            components=[],
                        ),
                        ChatInputForm(
                            submit_url=f"/api/chat/generate/{session_id}",
                            fire_page_event="chat-load",
                        ),
                    ],
                )
            ]

        @self.get(
            "/chat/history/{session_id}",
            response_model=FastUI,
            response_model_exclude_none=True,
        )
        async def chat_history(
            chat_session: Annotated[ChatSession, Depends(self.get_chat_session)],
        ) -> list[AnyComponent]:
            """
            Endpoint for showing the Chat History UI.
            """
            return [
                ChatMessage(msg.type, msg.content)
                for msg in chat_session.history.messages
            ]

        @self.post(
            "/chat/generate/{session_id}",
            response_model=FastUI,
            response_model_exclude_none=True,
        )
        async def chat_generate(
            user_msg: Annotated[str, Form(...)],
            session_id: Annotated[str, Path(title="The ChatHistory SessionID.")],
        ) -> list[AnyComponent]:
            """
            Endpoint for showing the Chat Generate UI.
            """
            return [
                ChatMessage("human", user_msg),
                c.ServerLoad(
                    path=f"/chat/generate/response/{session_id}?user_msg={user_msg}",
                    load_trigger=PageEvent(name="generate-response"),
                    components=[c.Text(text="...")],
                    sse=True,
                ),
                ChatInputForm(
                    submit_url="/api/chat/generate/" + session_id,
                    fire_page_event="generate-response",
                ),
            ]

        @self.get("/chat/generate/response/{session_id}")
        async def chat_generate_response(
            user_msg: str,
            session: Annotated[ChatSession, Depends(self.get_chat_session)],
        ) -> StreamingResponse:
            session.history.add_message(HumanMessage(content=user_msg))
            return StreamingResponse(
                stream_response_generator(user_msg, session),
                media_type="text/event-stream",
            )
