from fastui_chat import ChatUI, basic_chat_handler
from langchain_openai.chat_models import ChatOpenAI

handler = basic_chat_handler(llm=ChatOpenAI())

app = ChatUI(chat_handler=handler)

app.start_with_uvicorn()
