from typing import Any, Literal, TypedDict

from fastui import components as c
from fastui import events as e


class DisplayAlias(TypedDict):
    human: str
    ai: str


class ChatMessage(c.Div):
    """
    Component for displaying a chat message.
    """

    content: str
    msg_type: Literal["human", "ai"]
    class_name: str = "container col-sm-4 my-4"
    display_alias: DisplayAlias = {"human": "You", "ai": "ChatBot"}

    def __init__(
        self,
        msg_type: Literal["human", "ai"],
        content: str,
        **data: Any,
    ) -> None:
        data["msg_type"] = msg_type
        data["content"] = content
        super().__init__(**data, components=[])
        self.components = [
            c.Heading(text=self.display_alias[self.msg_type], level=6),
            c.Markdown(text=self.content),
        ]


class ChatInputForm(c.Form):
    """
    Component for displaying a chat input form.
    """

    fire_page_event: str
    display_mode: str = "inline"
    class_name: str = "row row-cols-lg-3 justify-content-center"
    form_fields: list[c.FormFieldInput] = [
        c.FormFieldInput(
            title="",
            name="user_msg",
            placeholder="Message ChatBot...",
            class_name="py-4",
        ),
    ]

    def __init__(
        self,
        *,
        submit_url: str,
        fire_page_event: str,
        **data: Any,
    ) -> None:
        data["submit_url"] = submit_url
        data["fire_page_event"] = fire_page_event
        super().__init__(**data, footer=[])
        self.footer = [
            c.FireEvent(event=e.PageEvent(name=self.fire_page_event)),
        ]
