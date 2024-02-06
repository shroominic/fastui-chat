from typing import Any, Literal, Union

from fastui import components as c
from fastui import events as e
from typing_extensions import TypedDict


class DisplayAlias(TypedDict):
    human: str
    ai: str


class ChatMessage(c.Div):
    """
    Component for displaying a chat message.
    """

    content: Union[str, list[Union[str, dict]]]
    msg_type: Literal["human", "ai"]
    class_name: str = "container mx-3 ms-1"
    display_alias: DisplayAlias = {"human": "You", "ai": "ChatBot"}

    @property
    def images(self) -> list[str]:
        """Return a list of image URLs in the message content."""
        if isinstance(self.content, str):
            return []
        return [
            (
                item["image_url"]["url"]
                if isinstance(item["image_url"], dict)
                else item["image_url"]
            )
            for item in self.content
            if isinstance(item, dict) and item["type"] == "image_url"
        ]

    @property
    def message(self) -> str:
        """Return the message content."""
        return (
            self.content
            if isinstance(self.content, str)
            else self.content[0]
            if isinstance(self.content[0], str)
            else self.content[0]["text"]
        )

    def __init__(
        self,
        msg_type: Literal["human", "ai"],
        content: Union[str, list[Union[str, dict]]],
        **data: Any,
    ) -> None:
        if msg_type == "AIMessageChunk":
            msg_type = "ai"
        data["msg_type"] = msg_type
        data["content"] = content
        super().__init__(**data, components=[])
        self.components = [
            c.Heading(text=self.display_alias[self.msg_type], level=6),
            c.Markdown(text=self.message),
            *(
                c.Image(
                    src=image_url,
                    class_name="img-fluid",
                )
                for image_url in self.images
            ),
        ]


class ChatInputForm(c.Form):
    """
    Component for displaying a chat input form.
    """

    fire_page_event: str
    display_mode: str = "inline"
    class_name: str = "row"
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
