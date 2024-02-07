from typing import Any

from fastapi import FastAPI
from langchain_core.chat_history import BaseChatMessageHistory

# todo rm langchain_openai import
from langchain_openai.chat_models import ChatOpenAI

from .chat import ChatAPIRouter
from .history import InMemoryChatMessageHistory, init_history_callable
from .runtime import router as core_router
from .session import basic_chat_handler as chat_handle_creator
from .types import ChatHandler, HistoryGetter


class ChatUI(FastAPI):
    def __init__(
        self,
        chat_handler: ChatHandler | None = None,
        history_backend: type[BaseChatMessageHistory] | None = None,
        history_backend_kwargs: dict[str, Any] = {},
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.history_getter: HistoryGetter = init_history_callable(
            history_backend or InMemoryChatMessageHistory, history_backend_kwargs
        )
        self.chat_handler = chat_handler or chat_handle_creator(
            llm=ChatOpenAI(), history_getter=self.history_getter
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
