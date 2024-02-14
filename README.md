# fastui-chat

[![Version](https://badge.fury.io/py/fastui-chat.svg)](https://badge.fury.io/py/fastui-chat)
![Downloads](https://img.shields.io/pypi/dm/fastui-chat)
[![license](https://img.shields.io/github/license/shroominic/fastui-chat.svg)](https://github.com/shroominic/fastui-chat/blob/main/LICENSE)
[![Twitter Follow](https://img.shields.io/twitter/follow/shroominic?style=social)](https://x.com/shroominic)

A minimalistic ChatBot Interface in pure python. </br>
Build on top of [FastUI](https://github.com/pydantic/FastUI) and [LangChain Core](https://github.com/langchain-ai/langchain).

## Usage

```bash
pip install fastui-chat
```

```python
from fastui_chat import ChatUI

# chatui inherits from FastAPI so you can use it as a FastAPI app
app = ChatUI()

# Run with:
# uvicorn examples.minimal:app

# for hot reloading:
# uvicorn examples.minimal:app --reload

# or use the built-in method
if __name__ == "__main__":
    app.start_with_uvicorn()
```

## Extend FastAPI

You can also only use the router and extend your existing FastAPI app.

```python
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
```

## Features

- Python Only
- Easy to use
- Minimalistic & Lightweight
- LangChain Compatible
- FastAPI Compatible
- Parallel Chat Sessions
- Switchable ChatHistory Backends
- Insert your custom chat handler

## Development Setup

```bash
git clone https://github.com/shroominic/fastui-chat.git && cd fastui-chat

./dev-install.sh
```

## Roadmap

If you want to contribute or see whats coming soon checkout the `roadmap.todo` file for open todos.
