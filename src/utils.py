import re
import textwrap
from textnode import TextNode, TextType
import pprint
from typing import List


def split_nodes_delimiter(old_nodes: List, delimiter, text_type):
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
                    intermediate_list.append(
                        TextNode(new_node, TextType.NORMAL_TEXT))

                current_is_delimited = not current_is_delimited

        # if the original string ended with relevant delimited text, the final
        # TextNode in the list will be empty, so just drop it
        if ends_with_delimited:
            final_nodes_list.extend(intermediate_list[:-1])
        else:
            final_nodes_list.extend(intermediate_list)

    return final_nodes_list


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.NORMAL_TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.NORMAL_TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.NORMAL_TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.NORMAL_TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        links = extract_markdown_links(original_text)
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.NORMAL_TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.NORMAL_TEXT))
    return new_nodes

def text_to_textnodes(text):
    nodes_list = [TextNode(text, TextType.NORMAL_TEXT)]
    nodes_list = split_nodes_delimiter(
        nodes_list, "**", TextType.BOLD_TEXT)
    nodes_list = split_nodes_delimiter(
        nodes_list, "*", TextType.ITALIC_TEXT)
    nodes_list = split_nodes_delimiter(
        nodes_list, "`", TextType.CODE)
    nodes_list = split_nodes_image(nodes_list)
    nodes_list = split_nodes_link(nodes_list)
    nodes_list = list(filter(lambda node: node.text, nodes_list))

    return nodes_list

def markdown_to_blocks(markdown):
    markdown = textwrap.dedent(markdown)
    blocks = markdown.split("\n\n")
    blocks = list(map(lambda x: x.strip(), blocks))
    blocks = list(filter(lambda x: x != "" and x != "\n" and x != " ", blocks))
    return blocks

def block_to_block_type(markdown_block):
    if re.match(r'^#{1,6}\s+.*$', markdown_block):
        return "heading"
    if re.match(r'^```.*```$', markdown_block, re.DOTALL):
        return "code"
    if re.match(r'^(>\s?.*\n?)+$', markdown_block):
        return "quote"
    if re.match(r'^(\s*[*-]\s.*\n?)+$', markdown_block):
        return "unordered_list"
    lines = markdown_block.strip().split("\n")
    if all(re.match(rf'^{i}\.\s.*$', line) for i, line in enumerate(lines, start=1)):
        return "ordered_list"
    else:
        return "paragraph"

