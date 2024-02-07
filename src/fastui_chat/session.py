from typing import Annotated, AsyncGenerator, Callable

from fastapi import Path
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from .history import InMemoryChatMessageHistory, init_history_callable
from .types import ChatHandler, HistoryGetter


class ChatSession:
    def __init__(
        self,
        *,
        session_id: str,
        chat_handler: ChatHandler,
        history_getter: HistoryGetter,
    ) -> None:
        self.session_id = session_id
        self.history = history_getter(session_id)
        self.chat_handler = chat_handler  # maybe make this chat_handler_getter

    async def astream(self, user_msg: str):
        async for message in self.chat_handler.astream(
            HumanMessage(content=user_msg),
            config={
                "run_name": "ChatMessage",
                "configurable": {"session_id": self.session_id},
            },
        ):
            yield message


def basic_chat_handler(
    llm: BaseChatModel,
    history_getter: HistoryGetter | None = None,
    system_message: str = "",
) -> ChatHandler:
    history_getter = history_getter or init_history_callable(InMemoryChatMessageHistory)
    handler = (
        ChatPromptTemplate.from_messages(
            [
                *(("system", system_message) if system_message else []),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{user_msg}"),
            ]
        )
        | llm
    )
    return {
        "user_msg": lambda x: x.content,
    } | RunnableWithMessageHistory(
        handler,
        get_session_history=history_getter,
        input_messages_key="user_msg",
        history_messages_key="history",
    )


def create_get_chat_session_dependency(
    history_getter: HistoryGetter,
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
