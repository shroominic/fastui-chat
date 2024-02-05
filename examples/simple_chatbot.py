from fastui_chat import ChatUI, basic_chat_handler
from funcchain.utils.memory import ChatMessageHistory
from langchain_openai.chat_models import ChatOpenAI

history = ChatMessageHistory()

handler = basic_chat_handler(
    llm=ChatOpenAI(),
    get_session_history=lambda session_id: history,
)

history.add_ai_message("How can I help you today?")

app = ChatUI(
    chat_history=history,
    chat_handler=handler,
)

app.start_with_uvicorn()
