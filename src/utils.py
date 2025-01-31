import re
import textwrap
from textnode import TextNode, TextType
from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode
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
            if len(new_node_list) % 2 != 1 and current_node.text[0] != delimiter:
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
    blocks = []
    current_block = []
    lines = markdown.split('\n')
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Empty line handling
        if not stripped:
            if current_block and not in_code_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            continue
        
        # Code block handling
        if stripped == '```':
            # If we're starting a code block, end the current block first
            if not in_code_block and current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            in_code_block = not in_code_block
            current_block.append(line)
            # If we're ending a code block, add it to blocks
            if not in_code_block:
                block = '\n'.join(current_block)
                print(f"DEBUG: Found code block:\n{block}")
                blocks.append(block)
                current_block = []
            continue
        
        # Inside code block
        if in_code_block:
            current_block.append(line)
            continue
        
        # Handle transitions between block types
        if current_block:
            last_line = current_block[-1].strip()
            # Start new block if:
            # 1. Current line is heading
            is_heading = re.match(r'^#{1,6} ', stripped)
            # 2. Current line starts list and previous wasn't list
            is_list = re.match(r'^[*-] ', stripped)
            was_list = re.match(r'^[*-] ', last_line)
            # 3. Current line is code block
            is_code = stripped == '```'
            
            if (is_heading or is_code or 
                (is_list and not was_list)):
                blocks.append('\n'.join(current_block))
                current_block = []
        
        current_block.append(line)
    
    if current_block:
        blocks.append('\n'.join(current_block))
    
    blocks = [b.strip() for b in blocks if b.strip()]
    print("DEBUG: All blocks:")
    for i, block in enumerate(blocks):
        print(f"Block {i}:\n{block}\n---")
    return blocks


def block_to_block_type(markdown_block):
    lines = markdown_block.split('\n')
    print(f"DEBUG: Checking block type for:\n{markdown_block}\n---")
    
    if re.match(r'^#{1,6} ', lines[0]):
        print("DEBUG: Found heading")
        return 'heading'
    if lines[0].strip() == '```' and lines[-1].strip() == '```':
        print("DEBUG: Found code block")
        return 'code'
    if all(line.startswith('>') for line in lines):
        print("DEBUG: Found quote")
        return 'quote'
    if all(re.match(r'^[*-] ', line) for line in lines):
        print("DEBUG: Found unordered list")
        return 'unordered_list'
    if all(re.match(r'^\d+\. ', line) for line in lines):
        print("DEBUG: Found ordered list")
        return 'ordered_list'
    print("DEBUG: Defaulting to paragraph")
    return 'paragraph'


def head_level(heading):
    # Count consecutive # at the start of the heading
    match = re.match(r'^(#+)\s', heading.strip())
    return len(match.group(1)) if match else 0

def text_to_children(text_block, block_type):
    match block_type:
        case "ul":
            # Remove list markers and leading/trailing whitespace
            return [re.sub(r'^[*-]\s*', '', line).strip() for line in text_block.split("\n")]
        case "ol":
            # Remove list markers and leading/trailing whitespace
            return [re.sub(r'^\d+\.\s*', '', line).strip() for line in text_block.split("\n")]
        case _:
            raise ValueError(f"Unsupported block type: {block_type}")

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    
    match block_type:
        case "heading":
            level = head_level(block)
            lines = block.split('\n')
            heading_line = lines[0]
            text = re.sub(r'^#+\s*', '', heading_line).strip()
            children = text_to_textnodes(text)
            html_children = [node.text_node_to_html_node() for node in children]
            return ParentNode(f"h{level}", html_children)
        
        case "code":
            lines = block.split('\n')
            
            # Remove ``` markers
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            
            # Find common indentation
            indents = []
            for line in lines:
                if line.strip():  # Ignore empty lines
                    indent = len(line) - len(line.lstrip())
                    indents.append(indent)
            
            # Get minimum indent (if any)
            min_indent = min(indents) if indents else 0
            
            # Remove common indentation and preserve the rest
            code_lines = []
            for line in lines:
                if line.strip():  # Non-empty line
                    code_lines.append(line[min_indent:])
                else:  # Empty line
                    code_lines.append('')
            
            code_text = '\n'.join(code_lines)
            return LeafNode("code", code_text, None, None)
        
        case "unordered_list":
            lines = block.split('\n')
            list_items = []
            for line in lines:
                if not line.strip():
                    continue
                # Remove list marker and leading space
                content = re.sub(r'^\s*[*-]\s*', '', line.strip())
                text_nodes = text_to_textnodes(content)
                html_children = [node.text_node_to_html_node() for node in text_nodes]
                list_items.append(ParentNode("li", html_children))
            return ParentNode("ul", list_items)
        
        case "ordered_list":
            lines = block.split('\n')
            list_items = []
            for line in lines:
                if not line.strip():
                    continue
                # Remove number, period, and leading space
                content = re.sub(r'^\s*\d+\.\s*', '', line.strip())
                text_nodes = text_to_textnodes(content)
                html_children = [node.text_node_to_html_node() for node in text_nodes]
                list_items.append(ParentNode("li", html_children))
            return ParentNode("ol", list_items)
        
        case "quote":
            lines = block.split('\n')
            quote_text = '\n'.join(line.lstrip('> ').strip() for line in lines)
            children = text_to_textnodes(quote_text)
            html_children = [node.text_node_to_html_node() for node in children]
            return ParentNode("blockquote", html_children)
        
        case "paragraph":
            children = text_to_textnodes(block)
            html_children = [node.text_node_to_html_node() for node in children]
            return ParentNode("p", html_children)
        
        case _:
            raise ValueError(f"Unsupported block type: {block_type}")

def markdown_to_html_node(markdown: str):
    # Normalize markdown
    markdown = markdown.strip()
    
    # Split into blocks
    blocks = markdown_to_blocks(markdown)
    
    # Convert blocks to HTML nodes
    children = []
    for block in blocks:
        if block.strip():  # Skip empty blocks
            child = block_to_html_node(block)
            children.append(child)
    
    # Wrap in a div
    return ParentNode("div", children)
