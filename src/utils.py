import os
import re
import shutil
from pathlib import Path
from enum import Enum
from typing import Callable
from typing import List
import textwrap
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
    stripped = line.strip()
    return stripped == '```' or (stripped.startswith('```') and not stripped.startswith('````'))

def is_heading(line: str) -> bool:
    """Check if a line is a markdown heading."""
    return bool(re.match(r'^#{1,6} ', line.strip()))

def is_list_item(line: str) -> bool:
    """Check if a line is a list item."""
    stripped = line.strip()
    return (bool(re.match(r'^[*-] ', stripped)) or
            bool(re.match(r'^\d+\.\s', stripped)))

def should_split_block(current_line: str, previous_line: str) -> bool:
    """Determine if we should split into a new block based on current and previous lines."""
    stripped_current = current_line.strip()
    stripped_previous = previous_line.strip() if previous_line else ''
    
    # Check for block transitions
    if is_heading(stripped_current) or is_code_marker(stripped_current):
        return True
        
    # Check for list transitions
    current_is_list = is_list_item(stripped_current)
    previous_is_list = is_list_item(stripped_previous)
    
    if current_is_list != previous_is_list:
        return True
        
    # Check for different list types
    if current_is_list and previous_is_list:
        current_ordered = bool(re.match(r'^\d+\.\s', stripped_current))
        previous_ordered = bool(re.match(r'^\d+\.\s', stripped_previous))
        return current_ordered != previous_ordered
        
    return False

def add_block(blocks: list, current_block: list) -> list:
    """Join and add the current block to blocks if non-empty."""
    if current_block:
        blocks.append('\n'.join(current_block))
    return []

def process_empty_line(blocks: list, current_block: list, in_code_block: bool) -> list:
    """Process an empty line, which typically indicates a block boundary unless in a code block."""
    if current_block and not in_code_block:
        return add_block(blocks, current_block)
    return current_block

def process_code_block_start(blocks: list, current_block: list, in_code_block: bool, line: str) -> tuple[list, bool]:
    """Handle the start or end of a code block marked by ```."""
    if not in_code_block and current_block:
        current_block = add_block(blocks, current_block)
    in_code_block = not in_code_block
    current_block.append(line)
    if not in_code_block:
        current_block = add_block(blocks, current_block)
    return current_block, in_code_block

def process_regular_line(blocks: list, current_block: list, line: str) -> list:
    """Process a regular line of text, checking for block type transitions."""
    if current_block and should_split_block(line, current_block[-1]):
        current_block = add_block(blocks, current_block)
    current_block.append(line)
    return current_block

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
            current_block = process_empty_line(blocks, current_block, in_code_block)
            continue
        
        # Code block handling
        if is_code_marker(line):
            current_block, in_code_block = process_code_block_start(blocks, current_block, in_code_block, line)
            continue
        
        # Inside code block
        if in_code_block:
            current_block.append(line)
            continue
        
        # Handle regular line with potential block transitions
        current_block = process_regular_line(blocks, current_block, line)
    
    # Add any remaining block
    if current_block:
        add_block(blocks, current_block)
    
    return [b.strip() for b in blocks if b.strip()]

def is_empty_block(block: str) -> bool:
    """Check if block is empty or whitespace only."""
    return not block.strip()

def is_heading_block(block: str) -> bool:
    """Check if block starts with 1-6 # characters followed by space."""
    return bool(re.match(r'^#{1,6} ', block.lstrip()))

def is_code_block(block: str) -> bool:
    """Check if block is wrapped in ``` markers."""
    stripped = block.strip()
    lines = stripped.split('\n')
    return len(lines) >= 2 and stripped.startswith('```') and stripped.endswith('```')

def get_non_empty_lines(block: str) -> list[str]:
    """Get list of non-empty lines from block."""
    return [line.strip() for line in block.split('\n') if line.strip()]

def is_quote_block(lines: list[str]) -> bool:
    """Check if all non-empty lines start with >."""
    return all(line.startswith('>') for line in lines)

def is_unordered_list_block(lines: list[str]) -> bool:
    """Check if all non-empty lines start with - or *."""
    return all(re.match(r'^[*-] ', line.strip()) for line in lines)

def is_ordered_list_block(lines: list[str]) -> bool:
    """Check if all non-empty lines start with a number followed by period."""
    return all(re.match(r'^\d+\. ', line.strip()) for line in lines)

def block_to_block_type(markdown_block: str) -> BlockType:
    """Determine the type of a markdown block based on its content and structure.
    
    Args:
        markdown_block: A string containing one or more lines of markdown text
        
    Returns:
        BlockType: The type of block (HEADING, CODE, QUOTE, etc.)
        
    The function checks for block types in this order:
    1. Empty block → PARAGRAPH
    2. Heading (# Text) → HEADING
    3. Code block (wrapped in ```) → CODE
    4. Quote (lines start with >) → QUOTE
    5. Unordered list (- or *) → UNORDERED_LIST
    6. Ordered list (1. 2. etc) → ORDERED_LIST
    7. Default → PARAGRAPH
    """
    if is_empty_block(markdown_block):
        return BlockType.PARAGRAPH
        
    if is_heading_block(markdown_block):
        return BlockType.HEADING
        
    if is_code_block(markdown_block):
        return BlockType.CODE
        
    # Get non-empty lines once for all remaining checks
    lines = get_non_empty_lines(markdown_block)
    
    if is_quote_block(lines):
        return BlockType.QUOTE
        
    if is_unordered_list_block(lines):
        return BlockType.UNORDERED_LIST
        
    if is_ordered_list_block(lines):
        return BlockType.ORDERED_LIST
        
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

def clean_unordered_list_item(line: str) -> str:
    """Remove - or * markers and clean whitespace from a list item.
    
    Args:
        line: A line from an unordered list (e.g., '- Item 1' or '* Item 1')
        
    Returns:
        str: Cleaned line with markers and extra whitespace removed
    """
    return re.sub(r'^\s*[*-]\s*', '', line.strip())

def clean_ordered_list_item(line: str) -> str:
    """Remove number markers and clean whitespace from a list item.
    
    Args:
        line: A line from an ordered list (e.g., '1. Item 1')
        
    Returns:
        str: Cleaned line with number marker and extra whitespace removed
    """
    return re.sub(r'^\s*\d+\.\s*', '', line.strip())

def split_into_lines(text: str) -> list[str]:
    """Split text into lines, handling different line endings.
    
    Args:
        text: Text block to split into lines
        
    Returns:
        list[str]: List of non-empty lines
    """
    # Replace Windows line endings with Unix line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return [line for line in text.split('\n')]

def process_list_block(text: str, clean_item_func: Callable[[str], str]) -> list[str]:
    """Process a list block using the provided cleaning function.
    
    Args:
        text: The list block text to process
        clean_item_func: Function to clean each list item
        
    Returns:
        list[str]: List of cleaned items
    """
    return [clean_item_func(line) for line in split_into_lines(text)]

def text_to_children(text_block: str, block_type: BlockType) -> list[str]:
    """Convert a text block into a list of child text elements based on block type.
    
    Args:
        text_block: The text content to process
        block_type: The type of block being processed
        
    Returns:
        list[str]: List of processed text items
        
    Raises:
        ValueError: If block_type is not supported
    """
    if block_type == BlockType.HEADING:
        # Remove heading markers
        return [re.sub(r'^#+\s*', '', text_block.strip())]
    elif block_type == BlockType.CODE:
        # Remove code markers and get content
        lines = text_block.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        return ['\n'.join(lines)]
    elif block_type == BlockType.QUOTE:
        # Remove quote markers
        lines = text_block.split('\n')
        return ['\n'.join(line.lstrip('> ').strip() for line in lines)]
    elif block_type == BlockType.UNORDERED_LIST:
        return process_list_block(text_block, clean_unordered_list_item)
    elif block_type == BlockType.ORDERED_LIST:
        return process_list_block(text_block, clean_ordered_list_item)
    elif block_type == BlockType.PARAGRAPH:
        return [text_block.strip()]
    
    raise ValueError(f"Unsupported block type: {block_type}")

def normalize_code_indentation(lines: list[str]) -> str:
    """Normalize indentation in code block lines.
    
    Args:
        lines: List of code lines
        
    Returns:
        str: Code text with normalized indentation
    """
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
    
    return '\n'.join(code_lines)

def convert_heading_block(block: str) -> HTMLNode:
    """Convert a heading block to an HTML node."""
    level = head_level(block)
    lines = block.split('\n')
    heading_line = lines[0]
    text = re.sub(r'^#+\s*', '', heading_line).strip()
    children = text_to_textnodes(text)
    html_children = [node.text_node_to_html_node() for node in children]
    return ParentNode(f"h{level}", html_children)

def convert_code_block(block: str) -> HTMLNode:
    """Convert a code block to an HTML node."""
    lines = block.split('\n')
    
    # Remove ``` markers
    if lines[0].startswith('```'):
        lines = lines[1:]
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
    
    code_text = normalize_code_indentation(lines)
    return LeafNode("code", code_text, None, None)

def convert_unordered_list(block: str) -> HTMLNode:
    """Convert an unordered list block to an HTML node."""
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

def convert_ordered_list(block: str) -> HTMLNode:
    """Convert an ordered list block to an HTML node."""
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

def convert_quote_block(block: str) -> HTMLNode:
    """Convert a quote block to an HTML node."""
    lines = block.split('\n')
    quote_text = '\n'.join(line.lstrip('> ').strip() for line in lines)
    children = text_to_textnodes(quote_text)
    html_children = [node.text_node_to_html_node() for node in children]
    return ParentNode("blockquote", html_children)

def convert_paragraph_block(block: str) -> HTMLNode:
    """Convert a paragraph block to an HTML node."""
    children = text_to_textnodes(block)
    html_children = []
    has_image = False
    image_node = None
    
    # First pass: collect nodes and check for image
    for node in children:
        html_node = node.text_node_to_html_node()
        if isinstance(html_node, LeafNode) and html_node.tag == 'img':
            has_image = True
            image_node = html_node
        html_children.append(html_node)
    
    # If there's exactly one image node and any other nodes are just empty text
    if has_image and all((
        isinstance(node, LeafNode) and 
        (node.tag == 'img' or (node.tag is None and not node.value.strip()))
    ) for node in html_children):
        return image_node
    
    return ParentNode("p", html_children)

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
            return convert_heading_block(block)
        case BlockType.CODE:
            return convert_code_block(block)
        case BlockType.UNORDERED_LIST:
            return convert_unordered_list(block)
        case BlockType.ORDERED_LIST:
            return convert_ordered_list(block)
        case BlockType.QUOTE:
            return convert_quote_block(block)
        case BlockType.PARAGRAPH:
            return convert_paragraph_block(block)
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

def copy_from_to_dir(source_dir: str, dest_dir: str):
    """
    Copy files and directories from source to destination.
    
    Args:
        source_dir (str): Source directory path
        dest_dir (str): Destination directory path
        
    Raises:
        ValueError: If source directory does not exist
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    # Check if source directory exists
    if not source_path.exists():
        raise ValueError(f"Source directory {source_path} does not exist")

    # Remove destination directory if it exists
    if dest_path.exists():
        shutil.rmtree(dest_path)

    # Create destination directory
    dest_path.mkdir(parents=True)

    # Iterate through all files and directories in source
    for item in source_path.iterdir():
        dest_item = dest_path / item.name
        
        if item.is_dir():
            # Recursively copy subdirectories
            copy_from_to_dir(str(item), str(dest_item))
        else:
            # Copy individual files, preserving symlinks
            if item.is_symlink():
                target = os.readlink(str(item))
                os.symlink(target, str(dest_item))
            else:
                shutil.copy2(str(item), str(dest_item))

def extract_title(markdown: str) -> str:
    for line in markdown.split("\n"):
        # Only match single # for h1 headers
        if line.strip().startswith('#') and not line.strip().startswith('##'):
            title = line.strip()[1:].strip()
            if title:
                return title
    
    return "Untitled"

def generate_page(from_path: str, template_path: str, dest_path: str):
    from_path = Path(from_path)
    template_path = Path(template_path)
    dest_path = Path(dest_path)

    with from_path.open('r') as from_file, \
         template_path.open('r') as template_file, \
         dest_path.open('w') as output_file:
        template = template_file.read()
        source_markdown = from_file.read()
        html_version = markdown_to_html_node(source_markdown)
        title = extract_title(source_markdown)
        new_document = template.replace("{{ Title }}", title).replace("{{ Content }}", str(html_version))
        output_file.write(new_document)

def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str):
    """
    Recursively generate HTML pages from markdown files.
    
    Args:
        dir_path_content (str): Path to the content directory containing markdown files
        template_path (str): Path to the HTML template file
        dest_dir_path (str): Destination directory for generated HTML files
    """
    content_path = Path(dir_path_content)
    dest_path = Path(dest_dir_path)
    template_path = Path(template_path)

    # Ensure destination directory exists
    dest_path.mkdir(parents=True, exist_ok=True)

    for dir_entry in content_path.iterdir():
        if dir_entry.is_dir():
            # Recursively process subdirectories
            subdir_dest = dest_path / dir_entry.name
            generate_pages_recursive(str(dir_entry), str(template_path), str(subdir_dest))
        elif dir_entry.suffix == '.md':
            # Generate HTML for markdown files
            relative_path = dir_entry.relative_to(content_path)
            output_path = dest_path / relative_path.with_suffix('.html')
            
            # Create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate the page
            generate_page(str(dir_entry), str(template_path), str(output_path))