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
from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory

from fastui_chat import ChatUI, basic_chat_handler

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
```

## Features

- Easy to use
- Minimalistic & Lightweight
- LangChain Compatible
- Python Only

## Development Setup

```bash
git clone https://github.com/shroominic/fastui-chat.git && cd fastui-chat

./dev-install.sh
```

## Roadmap

If you want to contribute or see whats coming soon checkout the `roadmap.todo` file for open todos.
