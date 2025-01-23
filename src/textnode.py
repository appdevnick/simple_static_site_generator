from enum import Enum
from leafnode import LeafNode
from typing import List

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
        return f"TextNode({self.text}, {self.text_type}, {self.url})"

    def text_node_to_html_node(self):
        match (self.text_type):
            case (TextType.NORMAL_TEXT):
                return LeafNode(None, self.text, None, None)
            case (TextType.BOLD_TEXT):
                return LeafNode("b", self.text, None, None)
            case (TextType.ITALIC_TEXT):
                return LeafNode("i", self.text, None, None)
            case (TextType.IMAGE):
                return LeafNode("img", "", None, {"src": self.url, "alt": self.text})
            case (TextType.LINK):
                return LeafNode("a", self.text, None, {"href": self.url})
            case (TextType.CODE):
                return LeafNode("code", self.text, None, None)
            case _:
                raise Exception(f"Unknown text_type: {self.text_type}")
            
    def split_nodes_delimiter(self, old_nodes: List, delimiter, text_type):
        final_nodes_list = []

        for current_node in old_nodes:
            intermediate_list = []
            if current_node.text_type != TextType.NORMAL_TEXT:
                final_nodes_list.append(current_node)
            else:
                starts_with_delimited = current_node.text[0] == delimiter
                ends_with_delimited = current_node.text[-1] == delimiter
                current_is_delimited = starts_with_delimited

                new_node_list = current_node.text.split(delimiter)

                # a proper number of delimiters will always end up with an odd-numbered list of nodes:
                if len(new_node_list) % 2 != 1:
                    raise Exception("Unclosed delimiter(s) in original text")

                # remove first item in list if the original string starts with a delimited phrase because
                # otherwise the resulting list will be screwed up
                if starts_with_delimited:
                    new_node_list = new_node_list[1:]

                for new_node in new_node_list:
                    if current_is_delimited:
                        intermediate_list.append(TextNode(new_node, text_type))
                    else:
                        intermediate_list.append(TextNode(new_node, TextType.NORMAL_TEXT))
                    
                    current_is_delimited = not current_is_delimited

            # if the original string ended with relevant delimited text, the final
            # TextNode in the list will be empty, so just drop it
            if ends_with_delimited:
                final_nodes_list.extend(intermediate_list[:-1])
            else:
                final_nodes_list.extend(intermediate_list)

        return final_nodes_list