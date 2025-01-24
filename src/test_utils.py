import unittest
from utils import markdown_to_blocks, extract_markdown_images, extract_markdown_links, split_nodes_link, split_nodes_image, text_to_textnodes
from textnode import TextNode, TextType

class TestTextNode(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

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
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
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
                TextNode("image", TextType.IMAGE, "https://www.example.COM/IMAGE.PNG"),
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
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
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
                TextNode("another link", TextType.LINK, "https://blog.boot.dev"),
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
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
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
                TextNode("This is text without any images.", TextType.NORMAL_TEXT),
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
                TextNode("This is text without any links.", TextType.NORMAL_TEXT),
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

if __name__ == "__main__":
    unittest.main()