from htmlnode import HTMLNode
from typing import List

class LeafNode(HTMLNode):
    def __init__(self, tag: str, value: str, children: List, props: dict):
        if children:
            raise Exception("Leaf Node was passed children")

        if not value:
            raise ValueError("Leaf Node was not given a value")

        super().__init__(tag, value, None, props)

    def to_html(self):
        if not self.tag:
            return f"{self.value}"
        else:
            return f"<{self.tag + self.props_to_html()}>{self.value}</{self.tag}>".strip()
