import unittest
from utils import markdown_to_html_node, extract_title, generate_page
from pathlib import Path
from tempfile import TemporaryDirectory


class TestMarkdownToHTMLIntegration(unittest.TestCase):
    def test_complex_markdown_conversion(self):
        markdown = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Subheading

- List item 1
- List item 2
  - Nested item
- List item 3

1. Ordered item 1
2. Ordered item 2
3. Ordered item 3

> This is a blockquote
> with multiple lines

```python
def hello():
    print("Hello, world!")
```

Here's a [link](https://example.com) and an ![image](image.jpg)."""

        html_node = markdown_to_html_node(markdown)
        html_str = str(html_node)

        # Check for various HTML elements
        self.assertIn("<h1>Main Title</h1>", html_str)
        self.assertTrue("<strong>bold</strong>" in html_str or "<b>bold</b>" in html_str)
        self.assertTrue("<em>italic</em>" in html_str or "<i>italic</i>" in html_str)
        self.assertIn("<h2>Subheading</h2>", html_str)
        self.assertIn("<ul>", html_str)
        self.assertIn("<ol>", html_str)
        self.assertIn("<blockquote>", html_str)
        self.assertIn("<code>", html_str)
        self.assertIn('<a href="https://example.com">link</a>', html_str)
        # Check image attributes separately since order doesn't matter
        self.assertIn('alt="image"', html_str)
        self.assertIn('src="image.jpg"', html_str)

    def test_nested_content(self):
        markdown = """# Title

1. Item with *italic*
2. Item with **bold**
   - Nested with `code`
   - More nested
3. Back to ordered

> Quote with **bold**
> And *italic*"""

        html_node = markdown_to_html_node(markdown)
        html_str = str(html_node)

        # Check nesting structure
        self.assertIn("<ol>", html_str)
        self.assertIn("<ul>", html_str)
        self.assertTrue("<em>italic</em>" in html_str or "<i>italic</i>" in html_str)
        self.assertTrue("<strong>bold</strong>" in html_str or "<b>bold</b>" in html_str)
        self.assertIn("<code>code</code>", html_str)

    def test_code_block_with_indentation(self):
        markdown = """```python
def example():
    if True:
        print('indented')
        print('properly')
```"""

        html_node = markdown_to_html_node(markdown)
        html_str = str(html_node)

        # Check if indentation is preserved
        self.assertIn("    if True:", html_str)
        self.assertIn("        print('indented')", html_str)

    def test_mixed_list_types(self):
        markdown = """1. First
2. Second
   - Sub 1
   - Sub 2
3. Third
   1. Sub ordered 1
   2. Sub ordered 2"""

        html_node = markdown_to_html_node(markdown)
        html_str = str(html_node)

        # Check list structure
        self.assertIn("<ol>", html_str)
        self.assertIn("<ul>", html_str)
        self.assertIn("First", html_str)
        self.assertIn("Sub 1", html_str)
        self.assertIn("Sub ordered 1", html_str)

    def test_title_extraction(self):
        markdown = """# Main Title

Content here

## Subheading"""
        
        title = extract_title(markdown)
        self.assertEqual(title, "Main Title")

    def test_title_extraction_no_title(self):
        markdown = """Content without title

## Subheading"""
        
        title = extract_title(markdown)
        self.assertEqual(title, "Untitled")

    def test_page_generation(self):
        with TemporaryDirectory() as temp_dir:
            # Create test files
            temp_path = Path(temp_dir)
            markdown_file = temp_path / "test.md"
            template_file = temp_path / "template.html"
            output_file = temp_path / "output.html"
            
            # Write test content
            markdown_file.write_text("""# Test Title

This is a test.""")
            
            template_file.write_text("""<!DOCTYPE html>
<html>
<head><title>{{ Title }}</title></head>
<body>
{{ Content }}
</body>
</html>""")
            
            # Generate page
            generate_page(str(markdown_file), str(template_file), str(output_file))
            
            # Check output
            output_content = output_file.read_text()
            self.assertIn("<title>Test Title</title>", output_content)
            self.assertIn("<h1>Test Title</h1>", output_content)
            self.assertIn("<p>This is a test.</p>", output_content)


if __name__ == '__main__':
    unittest.main()
