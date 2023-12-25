from typing import AsyncGenerator
from typing_extensions import TypedDict

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import Runnable

from .session import ChatSession


class FakeDatabase(TypedDict, total=False):
    chat_history: BaseChatMessageHistory
    chat_handler: Runnable


database: FakeDatabase = {}


def init_database(
    chat_history: BaseChatMessageHistory,
    chat_handler: Runnable,
) -> None:
    database["chat_history"] = chat_history
    database["chat_handler"] = chat_handler


# FastAPI Dependencies:


async def get_history() -> AsyncGenerator[BaseChatMessageHistory, None]:
    if "chat_history" not in database:
        raise RuntimeError("Database not initialized")
    yield database["chat_history"]


async def get_session() -> AsyncGenerator[ChatSession, None]:
    if "chat_history" not in database or "chat_handler" not in database:
        raise RuntimeError("Database not initialized")
    yield ChatSession(
        history=database["chat_history"],
        chat_handler=database["chat_handler"],
    )
