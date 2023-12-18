from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import prebuilt_html

from .chat import router as chat_router

app = FastAPI()
app.include_router(chat_router)


@app.get("/{path:path}", response_class=HTMLResponse)
async def html_landing() -> HTMLResponse:
    """
    Simple HTML page which serves the React app, comes last as it matches all paths.
    """
    return HTMLResponse(prebuilt_html(title="ChatBot"))


def start() -> None:
    import uvicorn

    uvicorn.run("fastui_chat.app:app", reload=True)


if __name__ == "__main__":
    start()
