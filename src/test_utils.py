import unittest
from pprint import pprint
from utils import (block_to_block_type, markdown_to_blocks, extract_markdown_images,
                  extract_markdown_links, markdown_to_html_node, split_nodes_link,
                  split_nodes_image, text_to_textnodes, BlockType, copy_from_to_dir, extract_title, generate_page)
from textnode import TextNode, TextType
import os
import shutil
import tempfile


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
        markdown = "# This is a heading\n\nThis is a paragraph of text. It has some **bold** and *italic* words inside of it.\n\n* This is the first list item in a list block\n* This is a list item\n* This is another list item"

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
        # Test different heading levels
        for i in range(1, 7):
            block = "#" * i + " This is a heading"
            block_type = block_to_block_type(block)
            self.assertEqual(block_type, BlockType.HEADING)

    def test_block_to_block_type_code(self):
        # Test basic code block
        block = "```\ncode block\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.CODE)
        
        # Test code block with language
        block = "```python\ncode block\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.CODE)

    def test_block_to_block_type_quote(self):
        # Test single line quote
        block = "> This is a quote"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.QUOTE)
        
        # Test multi-line quote
        block = "> This is a quote\n> with multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.QUOTE)
        
        # Test quote with mixed indentation
        block = ">This is a quote\n  > with mixed indentation"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.QUOTE)

    def test_block_to_block_type_unordered_list(self):
        # Test asterisk list
        block = "* Item 1\n* Item 2\n* Item 3"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.UNORDERED_LIST)
        
        # Test dash list
        block = "- Item 1\n- Item 2\n- Item 3"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.UNORDERED_LIST)
        
        # Test mixed indentation
        block = "* Item 1\n  * Subitem\n* Item 2"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ordered_list(self):
        # Test sequential numbers
        block = "1. First item\n2. Second item\n3. Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.ORDERED_LIST)
        
        # Test non-sequential numbers (should still work)
        block = "1. First item\n5. Second item\n10. Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.ORDERED_LIST)
        
        # Test with indentation
        block = "1. First item\n    2. Subitem\n3. Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.ORDERED_LIST)

    def test_block_to_block_type_paragraph(self):
        # Test simple paragraph
        block = "This is a paragraph of text."
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)
        
        # Test multi-line paragraph
        block = "This is a paragraph\nthat spans multiple\nlines of text."
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)
        
        # Test paragraph with inline formatting
        block = "This is a paragraph with **bold** and *italic* text."
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_block_to_block_type_code_with_indentation(self):
        block = "```\ndef example():\n    print('Hello')\n\nexample()\n```"
        node = markdown_to_html_node(block)
        html = node.to_html()
        self.assertIn('def example():', html)
        self.assertIn('    print(\'Hello\')', html)
        self.assertIn('example()', html)

    def test_markdown_to_html_nodes(self):
        self.maxDiff = None
        markdown = "# Heading Level 1\n\n## Heading Level 2\n\n> This is a blockquote.\n> It can span multiple lines.\n\n* Unordered list item 1\n* Unordered list item 2\n* Unordered list item 3\n\n- Another unordered list item\n- Yet another unordered list item\n\n1. Ordered list item 1\n2. Ordered list item 2\n3. Ordered list item 3"

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
        markdown = "# Heading\n\nThis is a paragraph with **bold** and *italic* text and a [link](https://example.com).\n\n![image](https://example.com/image.png)"
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

    def test_extract_title(self):
        markdown = "# My Simple Title\n\nThis is a plain sentence."
        title = extract_title(markdown)
        self.assertEqual(title, "My Simple Title")

class TestCopyFromToDir(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temporary directories
        shutil.rmtree(self.test_dir)

    def test_copy_directory_with_files(self):
        # Create source directory with files
        source_dir = os.path.join(self.test_dir, 'source')
        dest_dir = os.path.join(self.test_dir, 'destination')
        os.makedirs(source_dir)
        
        # Create some test files
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('test content 1')
        with open(os.path.join(source_dir, 'file2.txt'), 'w') as f:
            f.write('test content 2')
        
        # Copy directory
        copy_from_to_dir(source_dir, dest_dir)
        
        # Check destination directory contents
        self.assertTrue(os.path.exists(dest_dir))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, 'file1.txt')))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, 'file2.txt')))
        
        # Check file contents
        with open(os.path.join(dest_dir, 'file1.txt'), 'r') as f:
            self.assertEqual(f.read(), 'test content 1')
        with open(os.path.join(dest_dir, 'file2.txt'), 'r') as f:
            self.assertEqual(f.read(), 'test content 2')

    def test_copy_directory_with_subdirectories(self):
        # Create source directory with subdirectories and files
        source_dir = os.path.join(self.test_dir, 'source')
        dest_dir = os.path.join(self.test_dir, 'destination')
        os.makedirs(os.path.join(source_dir, 'subdir1'))
        os.makedirs(os.path.join(source_dir, 'subdir2'))
        
        # Create files in main directory and subdirectories
        with open(os.path.join(source_dir, 'main_file.txt'), 'w') as f:
            f.write('main file content')
        with open(os.path.join(source_dir, 'subdir1', 'sub_file1.txt'), 'w') as f:
            f.write('subdir1 file content')
        with open(os.path.join(source_dir, 'subdir2', 'sub_file2.txt'), 'w') as f:
            f.write('subdir2 file content')
        
        # Copy directory
        copy_from_to_dir(source_dir, dest_dir)
        
        # Check destination directory contents
        self.assertTrue(os.path.exists(dest_dir))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, 'main_file.txt')))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, 'subdir1', 'sub_file1.txt')))
        self.assertTrue(os.path.exists(os.path.join(dest_dir, 'subdir2', 'sub_file2.txt')))

    def test_non_existent_source_directory(self):
        # Try to copy a non-existent directory
        non_existent_dir = os.path.join(self.test_dir, 'non_existent')
        dest_dir = os.path.join(self.test_dir, 'destination')
        
        # Should raise a ValueError
        with self.assertRaises(ValueError):
            copy_from_to_dir(non_existent_dir, dest_dir)

    def test_overwrite_existing_destination(self):
        # Create source directory with files
        source_dir = os.path.join(self.test_dir, 'source')
        dest_dir = os.path.join(self.test_dir, 'destination')
        os.makedirs(source_dir)
        os.makedirs(dest_dir)
        
        # Create a file in destination to ensure it's overwritten
        with open(os.path.join(dest_dir, 'existing_file.txt'), 'w') as f:
            f.write('old content')
        
        # Create files in source
        with open(os.path.join(source_dir, 'file1.txt'), 'w') as f:
            f.write('new content')
        
        # Copy directory
        copy_from_to_dir(source_dir, dest_dir)
        
        # Check destination directory contents
        self.assertTrue(os.path.exists(os.path.join(dest_dir, 'file1.txt')))
        self.assertFalse(os.path.exists(os.path.join(dest_dir, 'existing_file.txt')))

class TestGeneratePage(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create a sample markdown file
        self.markdown_path = os.path.join(self.test_dir, 'test_page.md')
        with open(self.markdown_path, 'w') as f:
            f.write('# Test Page\n\nThis is a test markdown page.')
        
        # Create a sample template file
        self.template_path = os.path.join(self.test_dir, 'template.html')
        with open(self.template_path, 'w') as f:
            f.write('<!DOCTYPE html>\n<html>\n<body>\n{{content}}\n</body>\n</html>')
        
        # Create the public directory for output
        self.public_dir = os.path.join(self.test_dir, 'public')
        os.makedirs(self.public_dir, exist_ok=True)
        
        # Destination path for the generated HTML
        self.dest_path = os.path.join(self.public_dir, 'test_page.html')

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_generate_page(self):
        # Call the generate_page function
        generate_page(self.markdown_path, self.template_path, self.dest_path)
        
        # Check if the destination file was created
        self.assertTrue(os.path.exists(self.dest_path))
        
        # Read the generated HTML file
        with open(self.dest_path, 'r') as f:
            generated_html = f.read()
        
        # Check if the generated HTML contains expected content
        self.assertIn('<h1>Test Page</h1>', generated_html)
        self.assertIn('<p>This is a test markdown page.</p>', generated_html)
        self.assertTrue(generated_html.startswith('<!DOCTYPE html>'))
        self.assertTrue(generated_html.endswith('</html>'))
        
        # Explicitly check for template tag replacements
        self.assertNotIn('{{ Title }}', generated_html, "Title tag was not replaced")
        self.assertNotIn('{{ Content }}', generated_html, "Content tag was not replaced")

if __name__ == '__main__':
    unittest.main()
