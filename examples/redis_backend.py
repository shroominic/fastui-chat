from fastui_chat import ChatUI
from langchain_community.chat_message_histories import RedisChatMessageHistory

app = ChatUI(
    history_backend=RedisChatMessageHistory,
    history_backend_kwargs={"redis_url": "redis://localhost:6379/0"},
)

# Run with:
# $ uvicorn examples.redis_backend:app
