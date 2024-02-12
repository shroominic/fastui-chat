from fastapi import FastAPI
from fastui_chat import (
    InMemoryChatMessageHistory,
    create_chat_handler,
    create_history_factory,
)
from fastui_chat.chat import ChatAPIRouter
from fastui_chat.runtime import router as fastui_runtime

app = FastAPI()

history_getter = create_history_factory(InMemoryChatMessageHistory)
chat_handler = create_chat_handler(
    llm="ollama/open-hermes2", history_factory=history_getter
)

app.include_router(
    ChatAPIRouter(history_getter, chat_handler),
    prefix="/api",
)
app.include_router(fastui_runtime)

# start the server with `uvicorn examples.fastapi_router:app`
