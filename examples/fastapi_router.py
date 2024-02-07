from fastapi import FastAPI
from fastui_chat.chat import ChatAPIRouter
from fastui_chat.runtime import router as fastui_runtime
from funcchain.syntax.components.handler import create_chat_handler
from funcchain.utils.memory import InMemoryChatMessageHistory, create_history_factory

app = FastAPI()

history_getter = create_history_factory(InMemoryChatMessageHistory)
chat_handler = create_chat_handler(llm="gpt-4", history_getter=history_getter)

app.include_router(
    ChatAPIRouter(history_getter, chat_handler),
    prefix="/api",
)
app.include_router(fastui_runtime)

# start the server with `uvicorn examples.fastapi_router:app`
