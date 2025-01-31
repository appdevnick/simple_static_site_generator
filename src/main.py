from utils import markdown_to_html_node

def main():
    # A sample markdown string with various elements
    markdown = """
# Welcome to My Static Site Generator

This is a **simple** markdown *converter* for learning purposes.

## Features
- Easy to understand
- Supports basic markdown
- Great for learning

### Code Example
```
def hello_world():
    print("Learning is fun!")
```

> A wise quote about coding goes here.

Check out my [GitHub](https://github.com/example)!
"""

    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown)
    html_output = html_node.to_html()

    # Create an HTML file to visualize the output
    with open('markdown_demo.html', 'w') as f:
        f.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Markdown Conversion Demo</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .markdown-source, .html-output {{ 
            background-color: #f4f4f4; 
            border: 1px solid #ddd; 
            padding: 15px; 
            margin-bottom: 20px; 
            white-space: pre-wrap; 
        }}
    </style>
</head>
<body>
    <h1>Markdown to HTML Conversion</h1>
    
    <h2>Original Markdown</h2>
    <pre class="markdown-source">{markdown}</pre>
    
    <h2>Converted HTML</h2>
    <div class="html-output">{html_output}</div>
</body>
</html>
""")
    
    # Print out the HTML for terminal viewing
    print("Original Markdown:")
    print(markdown)
    print("\n--- Converted HTML ---")
    print(html_output)

if __name__ == "__main__":
    main()