from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import (
    FastUI,
    AnyComponent,
    prebuilt_html,
    components as c,
)
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory.buffer import ConversationBufferMemory
from langchain.schema.messages import AIMessage

app = FastAPI()

memory = ConversationBufferMemory()
chat = ConversationChain(llm=ChatOpenAI(), memory=memory)
memory.chat_memory.messages.append(
    AIMessage(content="How can I help you today?"),
)


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def chat_get(user_msg: str | None = None) -> list[AnyComponent]:
    """
    Show a table of users, `/api` is the endpoint the frontend will connect to
    when a user fixes `/` to fetch components to render.
    """
    if user_msg:
        await chat.apredict(input=user_msg)
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


@app.get("/{path:path}", response_class=HTMLResponse)
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="ChatBot"))


def start() -> None:
    import uvicorn

    uvicorn.run("fastui_chat.app:app", reload=True)
