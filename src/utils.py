import re
import textwrap
from enum import Enum
from typing import List
import os
import shutil

from textnode import TextNode, TextType
from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode

class BlockType(Enum):
    """Enum for different types of markdown blocks."""
    HEADING = 'heading'
    CODE = 'code'
    QUOTE = 'quote'
    UNORDERED_LIST = 'unordered_list'
    ORDERED_LIST = 'ordered_list'
    PARAGRAPH = 'paragraph'


def split_nodes_delimiter(old_nodes: List, delimiter, text_type):
    final_nodes_list = []

    for current_node in old_nodes:
        intermediate_list = []
        if current_node.text_type != TextType.NORMAL_TEXT:
            final_nodes_list.append(current_node)
            continue

        # If no delimiter in the text, just return the original node
        if delimiter not in current_node.text:
            final_nodes_list.append(current_node)
            continue

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


def is_code_marker(line: str) -> bool:
    """Check if a line is a code block marker (```)."""
    return line.strip() == '```'

def is_heading(line: str) -> bool:
    """Check if a line is a markdown heading."""
    return bool(re.match(r'^#{1,6} ', line.strip()))

def is_list_item(line: str) -> bool:
    """Check if a line is a list item."""
    return bool(re.match(r'^[*-] ', line.strip()))

def should_split_block(current_line: str, previous_line: str) -> bool:
    """Determine if we should split into a new block based on current and previous lines."""
    stripped_current = current_line.strip()
    stripped_previous = previous_line.strip() if previous_line else ''
    
    return (
        is_heading(stripped_current) or
        is_code_marker(stripped_current) or
        (is_list_item(stripped_current) and not is_list_item(stripped_previous))
    )

def add_block(blocks: list, current_block: list) -> list:
    """Join and add the current block to blocks if non-empty."""
    if current_block:
        blocks.append('\n'.join(current_block))
    return []

def markdown_to_blocks(markdown: str) -> list:
    """Split markdown content into logical blocks while preserving structure."""
    blocks = []
    current_block = []
    lines = markdown.split('\n')
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Empty line handling
        if not stripped:
            if current_block and not in_code_block:
                current_block = add_block(blocks, current_block)
            continue
        
        # Code block handling
        if is_code_marker(line):
            if not in_code_block and current_block:
                current_block = add_block(blocks, current_block)
            in_code_block = not in_code_block
            current_block.append(line)
            if not in_code_block:
                current_block = add_block(blocks, current_block)
            continue
        
        # Inside code block
        if in_code_block:
            current_block.append(line)
            continue
        
        # Handle transitions between block types
        if current_block and should_split_block(line, current_block[-1]):
            current_block = add_block(blocks, current_block)
        
        current_block.append(line)
    
    # Add any remaining block
    if current_block:
        add_block(blocks, current_block)
    
    return [b.strip() for b in blocks if b.strip()]


def block_to_block_type(markdown_block: str) -> BlockType:
    """Determine the type of a markdown block based on its content and structure.
    
    Args:
        markdown_block: A string containing one or more lines of markdown text
        
    Returns:
        str: The type of block, one of:
            - 'heading': A markdown heading (# to ######)
            - 'code': A code block wrapped in ```
            - 'quote': A blockquote starting with >
            - 'unordered_list': A list with - or * bullets
            - 'ordered_list': A numbered list (1., 2., etc)
            - 'paragraph': Any other type of text block
    """
    # Handle empty blocks
    if not markdown_block.strip():
        return BlockType.PARAGRAPH
    
    # Check for heading (must be at start)
    if re.match(r'^#{1,6} ', markdown_block.lstrip()):
        return BlockType.HEADING
    
    # Check for code block (must be wrapped in ```)
    lines = markdown_block.strip().split('\n')
    if len(lines) >= 2 and markdown_block.strip().startswith('```') and markdown_block.strip().endswith('```'):
        return BlockType.CODE
    
    # Check for blockquote (all non-empty lines must start with >)
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    if all(line.startswith('>') for line in non_empty_lines):
        return BlockType.QUOTE
    
    # Check for unordered list (all non-empty lines must start with - or *)
    if all(re.match(r'^[*-] ', line.strip()) for line in non_empty_lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list (all non-empty lines must start with number.)
    if all(re.match(r'^\d+\. ', line.strip()) for line in non_empty_lines):
        return BlockType.ORDERED_LIST
    
    # Default to paragraph if no other type matches
    return BlockType.PARAGRAPH


def head_level(heading: str) -> int:
    """Extract the heading level from a markdown heading.
    
    Args:
        heading: A string containing a markdown heading (e.g., '## Heading')
        
    Returns:
        int: The level of the heading (1-6)
    """
    match = re.match(r'^(#+)\s', heading.strip())
    return len(match.group(1)) if match else 0

def text_to_children(text_block: str, block_type: BlockType) -> List[str]:
    """Convert a text block into a list of child text elements based on block type.
    
    Args:
        text_block: The text content to process
        block_type: The type of block being processed
        
    Returns:
        List[str]: List of processed text items
        
    Raises:
        ValueError: If block_type is not supported
    """
    match block_type:
        case BlockType.UNORDERED_LIST:
            # Remove list markers and leading/trailing whitespace
            return [re.sub(r'^[*-]\s*', '', line).strip() for line in text_block.split("\n")]
        case BlockType.ORDERED_LIST:
            # Remove list markers and leading/trailing whitespace
            return [re.sub(r'^\d+\.\s*', '', line).strip() for line in text_block.split("\n")]
        case _:
            raise ValueError(f"Unsupported block type: {block_type}")

def block_to_html_node(block: str) -> HTMLNode:
    """Convert a markdown block to its corresponding HTML node.
    
    Args:
        block: A string containing a markdown block
        
    Returns:
        HTMLNode: Either a LeafNode or ParentNode representing the HTML structure
    """
    block_type = block_to_block_type(block)
    
    match block_type:
        case BlockType.HEADING:
            level = head_level(block)
            lines = block.split('\n')
            heading_line = lines[0]
            text = re.sub(r'^#+\s*', '', heading_line).strip()
            children = text_to_textnodes(text)
            html_children = [node.text_node_to_html_node() for node in children]
            return ParentNode(f"h{level}", html_children)
        
        case BlockType.CODE:
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
        
        case BlockType.UNORDERED_LIST:
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
        
        case BlockType.ORDERED_LIST:
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
        
        case BlockType.QUOTE:
            lines = block.split('\n')
            quote_text = '\n'.join(line.lstrip('> ').strip() for line in lines)
            children = text_to_textnodes(quote_text)
            html_children = [node.text_node_to_html_node() for node in children]
            return ParentNode("blockquote", html_children)
        
        case BlockType.PARAGRAPH:
            children = text_to_textnodes(block)
            html_children = []
            for node in children:
                html_node = node.text_node_to_html_node()
                if isinstance(html_node, LeafNode) and html_node.tag == 'img':
                    # Don't wrap images in paragraphs
                    return html_node
                html_children.append(html_node)
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

def copy_from_to_dir(source_dir: str, dest_dir: str) -> None:    
    if not os.path.exists(source_dir):
        raise ValueError(f"Source directory {source_dir} does not exist.")

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    os.mkdir(dest_dir)

    # List all entries in the source directory
    for entry in os.listdir(source_dir):
        # Full path of the source entry
        src_path = os.path.join(source_dir, entry)
        # Full path of the destination entry
        dest_path = os.path.join(dest_dir, entry)

        # If it's a file, copy the file
        if os.path.isfile(src_path):
            shutil.copy(src_path, dest_path)
        
        # If it's a directory, recursively copy the directory
        elif os.path.isdir(src_path):
            copy_from_to_dir(src_path, dest_path)

def extract_title(markdown: str) -> str:
    for line in markdown.split("\n"):
        matches = re.split(r"^#", line)
        if len(matches) > 1:
            return matches[1].strip()
        
    raise Exception("No h1 header found in document")

def generate_page(from_path: str, template_path: str, dest_path: str):
    with open(from_path, 'r') as from_file, open(template_path, 'r') as template_file, open(dest_path, 'w') as output_file:
        template = template_file.read()
        source_markdown = from_file.read()
        html_version = markdown_to_html_node(source_markdown)
        title = extract_title(source_markdown)
        new_document = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', template).replace("{{ Content }}", html_version.to_html())
        output_file.write(new_document)
