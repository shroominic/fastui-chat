from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from .history_factories import InMemoryChatMessageHistory, init_history_callable
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
