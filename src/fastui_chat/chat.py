from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory.buffer import ConversationBufferMemory

router = APIRouter()

memory = ConversationBufferMemory()
chat = ConversationChain(llm=ChatOpenAI(), memory=memory)

memory.chat_memory.add_ai_message("How can I help you today?")


@router.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def chat_ui(user_msg: str | None = None) -> list[AnyComponent]:
    """
    Main endpoint for showing the Chat UI and handling user input.
    """
    if user_msg:
        await chat.apredict(input=user_msg)

    return [
        c.Page(
            components=[
                c.ServerLoad(),
                c.Form(
                    submit_url=".",
                    method="GOTO",
                    form_fields=[
                        c.FormFieldInput(
                            title="",
                            name="user_msg",
                            placeholder="Message ChatBot...",
                            class_name="py-4",
                        ),
                    ],
                    footer=[],
                ),
            ],
        )
    ]


@router.get(
    "/api/chat_history", response_model=FastUI, response_model_exclude_none=True
)
async def chat_history() -> list[AnyComponent]:
    """
    Endpoint for showing the Chat History UI.
    """
    return [
        c.Page(
            components=[
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
            ],
        )
    ]
