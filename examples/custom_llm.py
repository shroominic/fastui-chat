from fastui_chat import ChatUI, basic_chat_handler

handler = basic_chat_handler(llm="gpt-4-0125-preview")

app = ChatUI(chat_handler=handler)

# manually start with:
# uvicorn examples.custom_llm:app

if __name__ == "__main__":
    # or with a method:
    app.start_with_uvicorn()
