import unittest
from utils import (
    split_into_lines,
    clean_unordered_list_item,
    clean_ordered_list_item,
    process_list_block,
    text_to_children,
    BlockType,
    is_heading,
    is_code_marker,
    is_list_item,
    should_split_block,
    is_empty_block,
    is_heading_block,
    is_code_block,
    is_quote_block,
    is_unordered_list_block,
    is_ordered_list_block,
)


class TestTextProcessing(unittest.TestCase):
    def test_split_into_lines_unix(self):
        text = "line1\nline2\nline3"
        lines = split_into_lines(text)
        self.assertEqual(lines, ["line1", "line2", "line3"])

    def test_split_into_lines_windows(self):
        text = "line1\r\nline2\r\nline3"
        lines = split_into_lines(text)
        self.assertEqual(lines, ["line1", "line2", "line3"])

    def test_split_into_lines_mixed(self):
        text = "line1\nline2\r\nline3"
        lines = split_into_lines(text)
        self.assertEqual(lines, ["line1", "line2", "line3"])

    def test_clean_unordered_list_item_dash(self):
        line = "- List item"
        cleaned = clean_unordered_list_item(line)
        self.assertEqual(cleaned, "List item")

    def test_clean_unordered_list_item_asterisk(self):
        line = "* List item"
        cleaned = clean_unordered_list_item(line)
        self.assertEqual(cleaned, "List item")

    def test_clean_unordered_list_item_indented(self):
        line = "  - List item"
        cleaned = clean_unordered_list_item(line)
        self.assertEqual(cleaned, "List item")

    def test_clean_ordered_list_item_basic(self):
        line = "1. List item"
        cleaned = clean_ordered_list_item(line)
        self.assertEqual(cleaned, "List item")

    def test_clean_ordered_list_item_multiple_digits(self):
        line = "10. List item"
        cleaned = clean_ordered_list_item(line)
        self.assertEqual(cleaned, "List item")

    def test_clean_ordered_list_item_indented(self):
        line = "  1. List item"
        cleaned = clean_ordered_list_item(line)
        self.assertEqual(cleaned, "List item")

    def test_process_list_block_unordered(self):
        text = "- Item 1\n- Item 2\n- Item 3"
        items = process_list_block(text, clean_unordered_list_item)
        self.assertEqual(items, ["Item 1", "Item 2", "Item 3"])

    def test_process_list_block_ordered(self):
        text = "1. Item 1\n2. Item 2\n3. Item 3"
        items = process_list_block(text, clean_ordered_list_item)
        self.assertEqual(items, ["Item 1", "Item 2", "Item 3"])

    def test_text_to_children_heading(self):
        text = "# Heading"
        children = text_to_children(text, BlockType.HEADING)
        self.assertEqual(children, ["Heading"])

    def test_text_to_children_code(self):
        text = "```\ncode\n```"
        children = text_to_children(text, BlockType.CODE)
        self.assertEqual(children, ["code"])

    def test_text_to_children_quote(self):
        text = "> Quote"
        children = text_to_children(text, BlockType.QUOTE)
        self.assertEqual(children, ["Quote"])

    def test_text_to_children_unordered_list(self):
        text = "- Item 1\n- Item 2"
        children = text_to_children(text, BlockType.UNORDERED_LIST)
        self.assertEqual(children, ["Item 1", "Item 2"])

    def test_text_to_children_ordered_list(self):
        text = "1. Item 1\n2. Item 2"
        children = text_to_children(text, BlockType.ORDERED_LIST)
        self.assertEqual(children, ["Item 1", "Item 2"])

    def test_text_to_children_paragraph(self):
        text = "Paragraph text"
        children = text_to_children(text, BlockType.PARAGRAPH)
        self.assertEqual(children, ["Paragraph text"])

    def test_is_heading_valid(self):
        self.assertTrue(is_heading("# Heading"))
        self.assertTrue(is_heading("## Heading"))
        self.assertTrue(is_heading("###### Heading"))

    def test_is_heading_invalid(self):
        self.assertFalse(is_heading("Heading"))
        self.assertFalse(is_heading("####### Heading"))
        self.assertFalse(is_heading("#Heading"))

    def test_is_code_marker(self):
        self.assertTrue(is_code_marker("```"))
        self.assertTrue(is_code_marker("```python"))
        self.assertFalse(is_code_marker("``"))
        self.assertFalse(is_code_marker("````"))

    def test_is_list_item(self):
        self.assertTrue(is_list_item("- Item"))
        self.assertTrue(is_list_item("* Item"))
        self.assertTrue(is_list_item("1. Item"))
        self.assertFalse(is_list_item("Item"))
        self.assertFalse(is_list_item("> Item"))

    def test_should_split_block(self):
        self.assertTrue(should_split_block("# Heading", "Text"))
        self.assertTrue(should_split_block("```", "Text"))
        self.assertFalse(should_split_block("Text", "Text"))

    def test_is_empty_block(self):
        self.assertTrue(is_empty_block(""))
        self.assertTrue(is_empty_block("  \n  \n  "))
        self.assertFalse(is_empty_block("Text"))

    def test_is_heading_block(self):
        self.assertTrue(is_heading_block("# Heading"))
        self.assertTrue(is_heading_block("### Heading"))
        self.assertFalse(is_heading_block("Heading"))
        self.assertFalse(is_heading_block("#Heading"))

    def test_is_code_block(self):
        self.assertTrue(is_code_block("```\ncode\n```"))
        self.assertTrue(is_code_block("```python\ncode\n```"))
        self.assertFalse(is_code_block("code"))
        self.assertFalse(is_code_block("```code"))

    def test_is_quote_block(self):
        self.assertTrue(is_quote_block(["> Quote"]))
        self.assertTrue(is_quote_block(["> Line 1", "> Line 2"]))
        self.assertFalse(is_quote_block(["Quote"]))
        self.assertFalse(is_quote_block(["> Line 1", "Line 2"]))

    def test_is_unordered_list_block(self):
        self.assertTrue(is_unordered_list_block(["- Item"]))
        self.assertTrue(is_unordered_list_block(["* Item"]))
        self.assertTrue(is_unordered_list_block(["- Item 1", "- Item 2"]))
        self.assertFalse(is_unordered_list_block(["Item"]))
        self.assertFalse(is_unordered_list_block(["- Item 1", "Item 2"]))

    def test_is_ordered_list_block(self):
        self.assertTrue(is_ordered_list_block(["1. Item"]))
        self.assertTrue(is_ordered_list_block(["1. Item 1", "2. Item 2"]))
        self.assertTrue(is_ordered_list_block(["1. Item 1", "10. Item 2"]))
        self.assertFalse(is_ordered_list_block(["Item"]))
        self.assertFalse(is_ordered_list_block(["1. Item 1", "Item 2"]))


if __name__ == '__main__':
    unittest.main()
