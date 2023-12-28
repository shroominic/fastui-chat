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
        chat_handler: Runnable[HumanMessage, AIMessage],
        history: BaseChatMessageHistory,
    ) -> None:
        self.history = history
        self.chat_handler = chat_handler

    async def astream(self, user_msg: str):
        async for message in self.chat_handler.astream(
            HumanMessage(content=user_msg),
            config={
                "run_name": "ChatMessage",
                "configurable": {"session_id": ""},
            },
        ):
            yield message


def basic_chat_handler(
    llm: BaseChatModel,
    chat_history: BaseChatMessageHistory,
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
        lambda _: chat_history,
        input_messages_key="user_msg",
        history_messages_key="history",
    )
