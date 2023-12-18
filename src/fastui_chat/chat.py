from fastapi import APIRouter, Form
from typing import Annotated
from fastui import AnyComponent, FastUI, components as c
from fastui.events import PageEvent
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory.buffer import ConversationBufferMemory

router = APIRouter()

memory = ConversationBufferMemory()
chat = ConversationChain(llm=ChatOpenAI(), memory=memory)

memory.chat_memory.add_ai_message("How can I help you today?")


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
            for msg in memory.chat_memory.messages
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
        c.ServerLoad(
            path="/chat/generate/result?user_msg=" + user_msg,
            load_trigger=PageEvent(name="generate-result"),
            components=[c.Text(text="...")],
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


@router.get(
    "/api/chat/generate/result",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def chat_generate_result(user_msg: str) -> list[AnyComponent]:
    """
    Endpoint for showing the Chat Generate Result UI.
    """
    await chat.apredict(input=user_msg)
    return [
        c.Div(
            components=[
                c.Heading(text="ChatBot", level=6),
                c.Text(text=memory.chat_memory.messages[-1].content),
            ],
            class_name="container col-sm-4 my-4",
        ),
    ]
