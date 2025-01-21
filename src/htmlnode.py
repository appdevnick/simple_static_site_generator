from typing import List
from functools import reduce

class HTMLNode:
    def __init__(self, tag: str, value: str, children: List, props: dict):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def to_html(self):
        # child classes should implement this themselves
        raise NotImplementedError

    def props_to_html(self):
        html_string = ""
        for prop, value in self.props.items():
            html_string += f" \"{prop}\"={value}"

        return html_string.strip()
        