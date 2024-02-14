from fastapi import FastAPI
from fastui_chat import create_chat_handler, create_history_factory
from fastui_chat.chat import ChatAPIRouter
from fastui_chat.history import InMemoryChatMessageHistory
from fastui_chat.runtime import router as fastui_runtime

# callable that returns a ChatMessageHistory given a session_id
history_factory = create_history_factory(
    # swap out with any from langchain_community.chat_message_histories
    InMemoryChatMessageHistory,
)

# a chat handler generates an AIMessage based on a given HumanMessage and ChatHistory
chat_handler = create_chat_handler(
    llm="openai/gpt-4-turbo-preview",
    history_factory=history_factory,
)

# setup your fastapi app
app = FastAPI()

# add the chatui router to your app
app.include_router(
    ChatAPIRouter(history_factory, chat_handler),
    prefix="/api",
)

# make sure to add the runtime router as latest since it has a catch-all route
app.include_router(fastui_runtime)

# start the server with `uvicorn examples.fastapi_router:app`
