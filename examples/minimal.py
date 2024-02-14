from fastui_chat import ChatUI

# chatui inherits from FastAPI so you can use it as a FastAPI app
app = ChatUI()

# Run with:
# uvicorn examples.minimal:app

# for hot reloading:
# uvicorn examples.minimal:app --reload
