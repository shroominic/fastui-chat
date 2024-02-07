from fastui_chat import ChatUI, basic_chat_handler

handler = basic_chat_handler(llm="gpt-4-0125-preview")

app = ChatUI(chat_handler=handler)

app.start_with_uvicorn()
