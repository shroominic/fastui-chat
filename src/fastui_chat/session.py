from typing import Annotated, AsyncGenerator, AsyncIterator, Callable

from fastapi import Path
from funcchain.schema.types import ChatHandler, ChatHistoryFactory
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.runnables import RunnableConfig


class ChatSession:  # RunnableBindingBase?
    def __init__(
        self,
        *,
        session_id: str,
        chat_handler: ChatHandler,
        history_getter: ChatHistoryFactory,
    ) -> None:
        self.session_id = session_id
        self.history = history_getter(session_id)
        self.chat_handler = chat_handler  # maybe make this chat_handler_getter

    @property
    def config(self) -> RunnableConfig:
        return {
            "run_name": "ChatMessage",
            "configurable": {
                "session_id": self.session_id,
            },
        }

    def invoke(self, msg: HumanMessage) -> AIMessage:
        return self.chat_handler.invoke(msg, self.config)

    async def ainvoke(self, msg: HumanMessage) -> AIMessage:
        return await self.chat_handler.ainvoke(msg, self.config)

    def stream(self, msg: HumanMessage) -> AsyncIterator[AIMessageChunk]:
        yield from self.chat_handler.stream(msg, self.config)

    async def astream(self, msg: HumanMessage) -> AsyncIterator[AIMessageChunk]:
        async for chunk in self.chat_handler.astream(msg, self.config):
            yield chunk


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
