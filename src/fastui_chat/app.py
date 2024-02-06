from typing import Any, Callable

from fastapi import FastAPI
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

# todo rm langchain_openai import
from langchain_openai.chat_models import ChatOpenAI

from .chat import ChatAPIRouter
from .fastui_core import router as core_router
from .history_factories import InMemoryChatMessageHistory, init_history_callable
from .session import basic_chat_handler as chat_handle_creator


class ChatUI(FastAPI):
    def __init__(
        self,
        chat_history_backend: type[BaseChatMessageHistory] | None = None,
        chat_handler: Callable[..., Runnable[HumanMessage, AIMessage]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.history_getter = init_history_callable(
            chat_history_backend or InMemoryChatMessageHistory
        )
        self.chat_handler = chat_handler or chat_handle_creator(
            llm=ChatOpenAI(), get_session_history=self.history_getter
        )
        self.include_router(
            ChatAPIRouter(
                history_getter=self.history_getter, chat_handler=self.chat_handler
            ),
            prefix="/api",
        )
        self.include_router(core_router)

    def start_with_uvicorn(self) -> None:
        try:
            import uvicorn
        except ImportError:
            print("Please install uvicorn with `pip install uvicorn`")
            exit(1)
        else:
            uvicorn.run(self)
