from typing import Callable

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory


class ChatSession:
    def __init__(
        self,
        *,
        session_id: str,
        chat_handler: Runnable[HumanMessage, AIMessage],
        history_getter: Callable[..., BaseChatMessageHistory],
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
    get_session_history: Callable[..., BaseChatMessageHistory],
    system_message: str = "",
) -> Runnable[HumanMessage, AIMessage]:
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
        get_session_history=get_session_history,
        input_messages_key="user_msg",
        history_messages_key="history",
    )
