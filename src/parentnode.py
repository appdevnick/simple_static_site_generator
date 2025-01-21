from htmlnode import HTMLNode
from functools import reduce
from typing import List


class ParentNode(HTMLNode):
    def __init__(self, tag: str, children: List, props: dict = None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if not self.tag:
            raise ValueError("No tag provided to a ParentNode")

        if not self.children:
            raise ValueError("No children provided to a ParentNode")

        else:
            children_string = ""
            for child in self.children:
                children_string += child.to_html()

            return f"<{self.tag}{self.props_to_html()}>{children_string}</{self.tag}>"
