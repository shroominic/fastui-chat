import asyncio
from fastapi import APIRouter, Form
from typing import Annotated
from fastui import AnyComponent, FastUI, components as c
from fastui.events import PageEvent
from sse_starlette import EventSourceResponse
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory

router = APIRouter()

memory = ChatMessageHistory(
    messages=[
        ChatMessage(content="How can I help you today?", role="ai")
    ]
)
model = ChatOllama()
prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    ("human", "{msg}")
])
chat_with_history = RunnableWithMessageHistory(
    prompt | model,
    lambda session_id: memory,  # session_id is always required
    input_messages_key="msg",
    history_messages_key="history",
)


@router.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def chat_ui() -> list[AnyComponent]:
    """
    Main endpoint for showing the Chat UI and handling user input.
    """
    return [
        c.Page(
            components=[
                c.ServerLoad(
                    path="/chat/history",
                    load_trigger=PageEvent(name="chat-load"),
                    components=[],
                ),
                c.Form(
                    submit_url="/api/chat/generate",
                    display_mode="inline",
                    form_fields=[
                        c.FormFieldInput(
                            title="",
                            name="user_msg",
                            placeholder="Message ChatBot...",
                            class_name="py-4",
                        ),
                    ],
                    footer=[
                        c.FireEvent(event=PageEvent(name="chat-load")),
                    ],
                ),
            ],
        )
    ]


@router.get(
    "/api/chat/history", response_model=FastUI, response_model_exclude_none=True
)
async def chat_history() -> list[AnyComponent]:
    """
    Endpoint for showing the Chat History UI.
    """
    return [
        *(
            c.Div(
                components=[
                    c.Heading(
                        text=("You" if msg.type != "ai" else "ChatBot"),
                        level=6,
                    ),
                    c.Text(text=msg.content),
                ],
                class_name="container col-sm-4 my-4",
            )
            for msg in memory.messages
        ),
    ]


@router.post(
    "/api/chat/generate", response_model=FastUI, response_model_exclude_none=True
)
async def chat_generate(user_msg: Annotated[str, Form(...)]) -> list[AnyComponent]:
    """
    Endpoint for showing the Chat Generate UI.
    """
    return [
        c.Div(
            components=[c.Heading(text="You", level=6), c.Text(text=user_msg)],
            class_name="container col-sm-4 my-4",
        ),
        c.Div(
            components=[
                c.Heading(text="ChatBot", level=6),
                c.ServerLoad(
                    path="/chat/generate/result?user_msg=" + user_msg,
                    load_trigger=PageEvent(name="generate-result"),
                    components=[c.Text(text="...")],
                    sse=True,
                ),
            ],
            class_name="container col-sm-4 my-4",
        ),
        c.Form(
            submit_url="/api/chat/generate",
            display_mode="inline",
            form_fields=[
                c.FormFieldInput(
                    title="",
                    name="user_msg",
                    placeholder="Message ChatBot...",
                    class_name="py-4",
                ),
            ],
            footer=[
                c.FireEvent(event=PageEvent(name="generate-result")),
            ],
        ),
    ]


async def stream(msg: str):
    """
    Stream model output as rendered FastUI component.
    """
    output = ""
    
    try:
        for chunk in chat_with_history.stream(
            input={"msg": msg},
            config={"configurable": {"session_id": "foo"}}
        ):
            output += chunk.content
            ui = FastUI(root=[c.Markdown(text=output)])
            res = ui.model_dump_json()
            yield res
    except Exception as e:
        yield e

    # avoid the browser reconnecting
    while True:
        yield res
        await asyncio.sleep(60)


@router.get(
    "/api/chat/generate/result",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def chat_generate_result(user_msg: str) -> list[AnyComponent]:
    """
    Endpoint for showing the Chat Generate Result UI.
    """
    return EventSourceResponse(stream(user_msg))