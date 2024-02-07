from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastui import prebuilt_html

router = APIRouter()


@router.get("/{path:path}", response_class=HTMLResponse)
async def fastui_runtime() -> HTMLResponse:
    """
    Core HTML page which serves the FastUI Runtime.
    """
    return HTMLResponse(
        prebuilt_html(title="ChatBot"),
    )
