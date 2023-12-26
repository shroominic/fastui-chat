from fastui_chat import ChatUI, basic_chat_handler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory

history = ChatMessageHistory()
handler = basic_chat_handler(
    llm=ChatOpenAI(),
    chat_history=history,
)

history.add_ai_message("How can I help you today?")

app = ChatUI(
    chat_history=history,
    chat_handler=handler,
)

app.start_with_uvicorn()
