from typing import Callable

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

ChatHandler = Runnable[HumanMessage, AIMessage]

HistoryGetter = Callable[..., BaseChatMessageHistory]
