import unittest
from pprint import pprint
from utils import block_to_block_type, markdown_to_blocks, extract_markdown_images, extract_markdown_links, markdown_to_html_node, split_nodes_link, split_nodes_image, text_to_textnodes
from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev)"
        )
        self.assertListEqual(
            [
                ("link", "https://boot.dev"),
                ("another link", "https://blog.boot.dev"),
            ],
            matches,
        )

    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.NORMAL_TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.NORMAL_TEXT),
                TextNode("image", TextType.IMAGE,
                         "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_image_single(self):
        node = TextNode(
            "![image](https://www.example.COM/IMAGE.PNG)",
            TextType.NORMAL_TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE,
                         "https://www.example.COM/IMAGE.PNG"),
            ],
            new_nodes,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.NORMAL_TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.NORMAL_TEXT),
                TextNode("image", TextType.IMAGE,
                         "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.NORMAL_TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev) with text that follows",
            TextType.NORMAL_TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.NORMAL_TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and ", TextType.NORMAL_TEXT),
                TextNode("another link", TextType.LINK,
                         "https://blog.boot.dev"),
                TextNode(" with text that follows", TextType.NORMAL_TEXT),
            ],
            new_nodes,
        )

    def test_text_to_text_nodes_list(self):
        text = f"This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"

        nodes = text_to_textnodes(text)

        desired_result = [
            TextNode("This is ", TextType.NORMAL_TEXT),
            TextNode("text", TextType.BOLD_TEXT),
            TextNode(" with an ", TextType.NORMAL_TEXT),
            TextNode("italic", TextType.ITALIC_TEXT),
            TextNode(" word and a ", TextType.NORMAL_TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.NORMAL_TEXT),
            TextNode("obi wan image", TextType.IMAGE,
                     "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.NORMAL_TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]

        self.assertListEqual(nodes, desired_result)

    def test_no_images(self):
        node = TextNode(
            "This is text without any images.",
            TextType.NORMAL_TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text without any images.",
                         TextType.NORMAL_TEXT),
            ],
            new_nodes,
        )

    def test_no_links(self):
        node = TextNode(
            "This is text without any links.",
            TextType.NORMAL_TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text without any links.",
                         TextType.NORMAL_TEXT),
            ],
            new_nodes,
        )

    def test_mixed_content(self):
        text = "This is **bold** and *italic* text with a [link](https://example.com) and an ![image](https://example.com/image.png)"
        nodes = text_to_textnodes(text)
        desired_result = [
            TextNode("This is ", TextType.NORMAL_TEXT),
            TextNode("bold", TextType.BOLD_TEXT),
            TextNode(" and ", TextType.NORMAL_TEXT),
            TextNode("italic", TextType.ITALIC_TEXT),
            TextNode(" text with a ", TextType.NORMAL_TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" and an ", TextType.NORMAL_TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/image.png"),
        ]
        self.assertListEqual(nodes, desired_result)

    def test_code_block(self):
        text = "This is a `code block` with text."
        nodes = text_to_textnodes(text)
        desired_result = [
            TextNode("This is a ", TextType.NORMAL_TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" with text.", TextType.NORMAL_TEXT),
        ]
        self.assertListEqual(nodes, desired_result)

    def test_single_block(self):
        markdown = "This is a single block of text."
        blocks = markdown_to_blocks(markdown)
        self.assertListEqual(["This is a single block of text."], blocks)

    def test_multiple_blocks(self):
        markdown = "This is the first block.\n\nThis is the second block."
        blocks = markdown_to_blocks(markdown)
        self.assertListEqual(
            ["This is the first block.", "This is the second block."], blocks
        )

    def test_blocks_with_whitespace(self):
        markdown = "  This is the first block.  \n\n  This is the second block.  "
        blocks = markdown_to_blocks(markdown)
        self.assertListEqual(
            ["This is the first block.", "This is the second block."], blocks
        )

    def test_empty_blocks(self):
        markdown = "\n\n"
        blocks = markdown_to_blocks(markdown)
        self.assertListEqual([], blocks)

    def test_mixed_content_blocks(self):
        markdown = "This is **bold** text.\n\nThis is *italic* text.\n\nThis is a [link](https://example.com)."
        blocks = markdown_to_blocks(markdown)
        self.assertListEqual(
            [
                "This is **bold** text.",
                "This is *italic* text.",
                "This is a [link](https://example.com).",
            ],
            blocks,
        )

    def test_complex_markdown(self):
        markdown = """
        # This is a heading
        
        This is a paragraph of text. It has some **bold** and *italic* words inside of it.

        * This is the first list item in a list block
        * This is a list item
        * This is another list item
        """

        blocks = markdown_to_blocks(markdown)
        self.assertListEqual(
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                "* This is the first list item in a list block\n* This is a list item\n* This is another list item"
            ],
            blocks,
        )

    def test_block_to_block_type_heading(self):
        block = "# This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, "heading")

    def test_block_to_block_type_code(self):
        block = "```\ncode block\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, "code")

    def test_block_to_block_type_quote(self):
        block = "> This is a quote\n> with multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, "blockquote")

    def test_block_to_block_type_unordered_list(self):
        block = "* Item 1\n* Item 2\n* Item 3"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, "unordered_list")

    def test_block_to_block_type_ordered_list(self):
        block = "1. First item\n2. Second item\n3. Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, "ordered_list")

    def test_block_to_block_type_paragraph(self):
        block = "This is a paragraph of text."
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, "paragraph")

    def test_block_to_block_type_mixed_content(self):
        block = "This is a paragraph with **bold** and *italic* text."
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, "paragraph")

    def test_markdown_to_html_nodes(self):
        self.maxDiff = None
        markdown = """
        # Heading Level 1

        ## Heading Level 2

        > This is a blockquote.
        > It can span multiple lines.

        * Unordered list item 1
        * Unordered list item 2
        * Unordered list item 3

        - Another unordered list item
        - Yet another unordered list item

        1. Ordered list item 1
        2. Ordered list item 2
        3. Ordered list item 3
        """

        node = markdown_to_html_node(markdown)
        to_html = node.to_html()
        self.assertEqual(
            str(to_html),
            str("<div><h1>Heading Level 1</h1><h2>Heading Level 2</h2><blockquote>This is a blockquote.\nIt can span multiple lines.</blockquote><ul><li>Unordered list item 1</li><li>Unordered list item 2</li><li>Unordered list item 3</li></ul><ul><li>Another unordered list item</li><li>Yet another unordered list item</li></ul><ol><li>Ordered list item 1</li><li>Ordered list item 2</li><li>Ordered list item 3</li></ol></div>")
        )

    def test_markdown_to_html_nodes_with_code(self):
        markdown = """
        ```
        def hello_world():
            print("Hello, world!")
        ```
        """
        node = markdown_to_html_node(markdown)
        to_html = node.to_html()
        
        # Check the structure and content, not exact whitespace
        self.assertTrue(to_html.startswith('<div>'), "HTML should start with a div")
        self.assertTrue(to_html.endswith('</div>'), "HTML should end with a div")
        
        # Extract the code content
        code_content = to_html[len('<div><code>'):-len('</code></div>')]
        
        # Check the code content
        self.assertIn('def hello_world():', code_content)
        self.assertIn('print("Hello, world!")', code_content)
        
        # Verify it's a code block
        self.assertIn('<code>', to_html)
        self.assertIn('</code>', to_html)

    def test_markdown_to_html_nodes_with_mixed_content(self):
        markdown = """
        # Heading

        This is a paragraph with **bold** and *italic* text and a [link](https://example.com).

        ![image](https://example.com/image.png)
        """
        node = markdown_to_html_node(markdown)
        to_html = node.to_html()
        self.assertEqual(
            to_html,
            '<div><h1>Heading</h1><p>This is a paragraph with <b>bold</b> and <i>italic</i> text and a <a href="https://example.com">link</a>.</p><img src="https://example.com/image.png" alt="image"/></div>'
        )

    def test_markdown_to_html_node(self):
        # Test a markdown string with various text types
        markdown = """# Heading 1

This is a **bold** and *italic* text with some `code`.

- List item 1
- List item 2

> A blockquote example"""

        html_node = markdown_to_html_node(markdown)
        html_string = html_node.to_html()
        
        # Check for presence of key HTML elements
        self.assertIn("<h1>Heading 1</h1>", html_string)
        self.assertIn("<b>bold</b>", html_string)
        self.assertIn("<i>italic</i>", html_string)
        self.assertIn("<code>code</code>", html_string)
        self.assertIn("<li>List item 1</li>", html_string)
        self.assertIn("<blockquote>", html_string)
        
        # Ensure no raw TextType representations are in the output
        self.assertNotIn("TextType.", html_string)

if __name__ == "__main__":
    unittest.main()
