from typing import Annotated, AsyncGenerator, Callable

from fastapi import Path
from funcchain.schema.types import ChatHandler, ChatHistoryFactory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.base import RunnableBindingBase


class ChatSession(RunnableBindingBase):
    history: BaseChatMessageHistory

    def __init__(
        self,
        *,
        session_id: str,
        chat_handler: ChatHandler,
        history_getter: ChatHistoryFactory,
    ) -> None:
        super().__init__(
            bound=chat_handler,
            config={
                "run_name": "ChatMessage",
                "configurable": {
                    "session_id": session_id,
                },
            },
            history=history_getter(session_id),
        )


def create_get_chat_session_dependency(
    history_getter: ChatHistoryFactory,
    chat_handler: ChatHandler,
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
