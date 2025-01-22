from enum import Enum
from leafnode import LeafNode

class TextType(Enum):
    NORMAL_TEXT = "normal text",
    BOLD_TEXT = "bold text"
    ITALIC_TEXT = "italic text"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str=None):
        self.text: str = text
        self.text_type: TextType = text_type
        self.url: str = url

    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

    def text_node_to_html_node(self):
        match (self.text_type):
            case (TextType.NORMAL_TEXT):
                return LeafNode(None, self.text)
            case (TextType.BOLD_TEXT):
                return LeafNode("b", self.text)
            case (TextType.ITALIC_TEXT):
                return LeafNode("i", self.text)
            case (TextType.IMAGE):
                return LeafNode("img", None, None, {"src": {self.url}, "alt": {self.text}})
            case (TextType.LINK):
                return LeafNode("a", self.text, None, {"href": {self.url}})
            case (TextType.CODE):
                return LeafNode("code", self.text, None, None)
            case _:
                raise Exception(f"Unknown text_type: {self.text_type}")