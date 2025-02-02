import unittest
from utils import (
    convert_heading_block,
    convert_code_block,
    convert_unordered_list,
    convert_ordered_list,
    convert_quote_block,
    convert_paragraph_block,
    block_to_html_node,
    BlockType,
)
from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode


class TestBlockConversion(unittest.TestCase):
    def test_heading_block_basic(self):
        block = "# Heading 1"
        node = convert_heading_block(block)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "h1")
        self.assertEqual(node.children[0].value, "Heading 1")

    def test_heading_block_with_formatting(self):
        block = "## This is a **bold** heading"
        node = convert_heading_block(block)
        self.assertEqual(node.tag, "h2")
        self.assertEqual(len(node.children), 3)  # "This is a ", "bold", and " heading"
        self.assertEqual(node.children[1].value, "bold")

    def test_heading_levels(self):
        for i in range(1, 7):
            block = "#" * i + f" Heading {i}"
            node = convert_heading_block(block)
            self.assertEqual(node.tag, f"h{i}")

    def test_code_block_basic(self):
        block = "```\nprint('hello')\n```"
        node = convert_code_block(block)
        self.assertIsInstance(node, LeafNode)
        self.assertEqual(node.tag, "code")
        self.assertEqual(node.value, "print('hello')")

    def test_code_block_with_indentation(self):
        block = "```\n    def hello():\n        print('hello')\n```"
        node = convert_code_block(block)
        self.assertEqual(node.value, "def hello():\n    print('hello')")

    def test_code_block_empty_lines(self):
        block = "```\ndef hello():\n\n    print('hello')\n\n```"
        node = convert_code_block(block)
        self.assertEqual(node.value, "def hello():\n\n    print('hello')\n")

    def test_unordered_list_basic(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        node = convert_unordered_list(block)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "ul")
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].children[0].value, "Item 1")

    def test_unordered_list_with_formatting(self):
        block = "- Normal item\n- **Bold** item\n- *Italic* item"
        node = convert_unordered_list(block)
        self.assertEqual(len(node.children), 3)  # Three list items
        bold_item = node.children[1]  # Second list item
        self.assertEqual(bold_item.children[0].value, "Bold")

    def test_unordered_list_with_empty_lines(self):
        block = "- Item 1\n\n- Item 2"
        node = convert_unordered_list(block)
        self.assertEqual(len(node.children), 2)

    def test_ordered_list_basic(self):
        block = "1. First\n2. Second\n3. Third"
        node = convert_ordered_list(block)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "ol")
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].children[0].value, "First")

    def test_ordered_list_with_formatting(self):
        block = "1. Normal item\n2. **Bold** item\n3. *Italic* item"
        node = convert_ordered_list(block)
        self.assertEqual(len(node.children), 3)  # Three list items
        bold_item = node.children[1]  # Second list item
        self.assertEqual(bold_item.children[0].value, "Bold")

    def test_ordered_list_non_sequential_numbers(self):
        block = "1. First\n5. Second\n10. Third"
        node = convert_ordered_list(block)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[2].children[0].value, "Third")

    def test_quote_block_basic(self):
        block = "> This is a quote"
        node = convert_quote_block(block)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "blockquote")
        self.assertEqual(node.children[0].value, "This is a quote")

    def test_quote_block_multiline(self):
        block = "> Line 1\n> Line 2\n> Line 3"
        node = convert_quote_block(block)
        self.assertEqual(node.children[0].value, "Line 1\nLine 2\nLine 3")

    def test_quote_block_with_formatting(self):
        block = "> This is a **bold** quote with *italic* text"
        node = convert_quote_block(block)
        self.assertEqual(len(node.children), 5)  # "This is a ", "bold", " quote with ", "italic", " text"

    def test_paragraph_block_basic(self):
        block = "This is a paragraph"
        node = convert_paragraph_block(block)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.children[0].value, "This is a paragraph")

    def test_paragraph_with_formatting(self):
        block = "This is a **bold** paragraph with *italic* text"
        node = convert_paragraph_block(block)
        self.assertEqual(len(node.children), 5)  # "This is a ", "bold", " paragraph with ", "italic", " text"

    def test_paragraph_with_image(self):
        # Test case 1: Standalone image
        block = "![alt](image.jpg)"
        node = convert_paragraph_block(block)
        self.assertIsInstance(node, LeafNode)  # Should return image node directly
        self.assertEqual(node.tag, "img")
        
        # Test case 2: Image with surrounding text
        block = "Text with ![alt](image.jpg)"
        node = convert_paragraph_block(block)
        self.assertIsInstance(node, ParentNode)  # Should be wrapped in paragraph
        self.assertEqual(node.tag, "p")
        self.assertEqual(len(node.children), 2)  # Text node and image node

    def test_paragraph_with_link(self):
        block = "Text with [link](https://example.com)"
        node = convert_paragraph_block(block)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.children[1].tag, "a")

    def test_block_to_html_node_all_types(self):
        test_blocks = {
            "# Heading": "h1",
            "```\ncode\n```": "code",
            "- List item": "ul",
            "1. List item": "ol",
            "> Quote": "blockquote",
            "Normal text": "p",
        }
        for block, expected_tag in test_blocks.items():
            node = block_to_html_node(block)
            self.assertEqual(node.tag, expected_tag)


if __name__ == "__main__":
    unittest.main()
