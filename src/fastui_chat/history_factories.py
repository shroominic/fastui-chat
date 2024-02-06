from typing import Annotated, AsyncGenerator, Awaitable, Callable

from fastapi import Path
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import Runnable
from rich import print

from .session import ChatSession

_in_memory_database: dict[str, list[BaseMessage]] = {}


class InMemoryChatMessageHistory(BaseChatMessageHistory):
    """In memory implementation of chat message history.

    Stores messages in an in memory list.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        if session_id not in _in_memory_database:
            _in_memory_database[session_id] = []

    @property
    def messages(self) -> list[BaseMessage]:
        return _in_memory_database[self.session_id]

    def add_message(self, message: BaseMessage) -> None:
        print(f"Adding message to {self.session_id}")
        _in_memory_database[self.session_id].append(message)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        print(f"Adding messages to {self.session_id}")
        _in_memory_database[self.session_id].extend(messages)

    def clear(self) -> None:
        print(f"Clearing {self.session_id}")
        del _in_memory_database[self.session_id][:]


def init_history_callable(
    backend: type[BaseChatMessageHistory],
) -> Callable[..., BaseChatMessageHistory]:
    """
    Create a function that returns a chat history.
    """

    def history_getter(session_id: str) -> BaseChatMessageHistory:
        return backend(session_id)

    return history_getter


def init_chat_handler_callable(
    handlers: dict[str, Callable[..., Awaitable[ChatSession]]],
) -> Callable[..., Awaitable[ChatSession]]:
    """
    Create a function that returns a chat handler.
    """

    async def chat_handler_getter(key: str = "default") -> ChatSession:
        return await handlers[key]()

    return chat_handler_getter


def create_get_chat_session_dependency(
    history_getter: Callable[..., BaseChatMessageHistory],
    chat_handler: Runnable[HumanMessage, AIMessage],
) -> Callable[[str], AsyncGenerator[ChatSession, None]]:
    """
    Create a dependency that returns a chat session.
    """

    async def get_chat_session(
        session_id: Annotated[str, Path(title="The ChatHistory SessionID.")],
    ) -> AsyncGenerator[ChatSession, None]:
        yield ChatSession(
            session_id=session_id,
            chat_handler=chat_handler,
            history_getter=history_getter,
        )

    return get_chat_session