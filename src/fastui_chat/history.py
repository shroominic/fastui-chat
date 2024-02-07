from typing import Any

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from rich import print

from .types import HistoryGetter

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
        _in_memory_database[self.session_id].append(message)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        _in_memory_database[self.session_id].extend(messages)

    def clear(self) -> None:
        print(f"Clearing {self.session_id}")
        del _in_memory_database[self.session_id][:]


def init_history_callable(
    backend: type[BaseChatMessageHistory],
    backend_kwargs: dict[str, Any] = {},
) -> HistoryGetter:
    """
    Create a function that returns a chat history.
    """

    def history_getter(session_id: str, **kwargs: Any) -> BaseChatMessageHistory:
        kwargs.update(backend_kwargs)
        return backend(session_id, **kwargs)

    return history_getter
