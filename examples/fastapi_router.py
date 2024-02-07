from fastapi import FastAPI
from fastui_chat.chat import ChatAPIRouter
from fastui_chat.history import InMemoryChatMessageHistory, init_history_callable
from fastui_chat.runtime import router as fastui_runtime
from fastui_chat.session import basic_chat_handler
from langchain_openai.chat_models import ChatOpenAI

app = FastAPI()

history_getter = init_history_callable(InMemoryChatMessageHistory)
chat_handler = basic_chat_handler(llm=ChatOpenAI(), history_getter=history_getter)

app.include_router(
    ChatAPIRouter(history_getter, chat_handler),
    prefix="/api",
)
app.include_router(fastui_runtime)

# start the server with `uvicorn examples.fastapi_router:app`
