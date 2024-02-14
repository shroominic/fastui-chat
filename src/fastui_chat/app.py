from typing import Any

from fastapi import FastAPI
from funcchain.schema.types import ChatHandler, ChatHistoryFactory
from funcchain.syntax.components.handler import create_chat_handler
from funcchain.utils.memory import InMemoryChatMessageHistory, create_history_factory
from langchain_core.chat_history import BaseChatMessageHistory

from .chat import ChatAPIRouter
from .runtime import router as core_router


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
        self.history_getter: ChatHistoryFactory = create_history_factory(
            history_backend or InMemoryChatMessageHistory,
            history_backend_kwargs,
        )
        self.chat_handler = chat_handler or create_chat_handler(
            llm="gpt-4-0125-preview",
            history_getter=self.history_getter,
        )
        self.include_router(
            ChatAPIRouter(
                history_getter=self.history_getter,
                chat_handler=self.chat_handler,
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
