# fastui-chat

A minimalistic ChatBot Interface in pure python.

## Usage

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
> git clone https://github.com/shroominic/fastui-chat.git && cd fastui-chat

> ./dev-install.sh

> startapp
```

## TODO

- [ ] Image IO (vision models)

- [ ] Store previous chats and display them

- [ ] AutoScroll to bottom of chat on new message

- [ ] Make easy to deploy

- [ ] Add tests

- [ ] Add more examples

- [ ] ... other ideas? Open an issue or PR!
