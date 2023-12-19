from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSerializable
from langchain_core.runnables.history import RunnableWithMessageHistory


class ChatSession:
    def __init__(
        self,
        *,
        chat_handler: RunnableSerializable,
        history: BaseChatMessageHistory,
    ) -> None:
        self.history = history
        self.history.add_ai_message("How can I help you today?")
        self.chain = RunnableWithMessageHistory(
            chat_handler,
            lambda session_id: self.history,
            input_messages_key="user_msg",
            history_messages_key="history",
        )

    async def astream(self, user_msg: str):
        async for message in self.chain.astream(
            {"user_msg": user_msg}, config={"configurable": {"session_id": ""}}
        ):
            yield message


def create_basic_chat_handler(llm: BaseChatModel, system_message: str = ""):
    return (
        ChatPromptTemplate.from_messages(
            [
                *(("system", system_message) if system_message else []),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{user_msg}"),
            ]
        )
        | llm
    )
