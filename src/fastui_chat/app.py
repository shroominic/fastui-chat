from typing import Any

from fastapi import FastAPI
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from .chat import router as chat_router
from .db import init_database
from .fastui_core import router as core_router


class ChatUI(FastAPI):
    def __init__(
        self,
        chat_history: BaseChatMessageHistory,
        chat_handler: Runnable[HumanMessage, AIMessage],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        init_database(chat_history, chat_handler)
        self.include_router(chat_router, prefix="/api")
        self.include_router(core_router)

    def start_with_uvicorn(self) -> None:
        try:
            import uvicorn
        except ImportError:
            print("Please install uvicorn with `pip install uvicorn`")
            exit(1)
        else:
            uvicorn.run(self)
