# Simple Static Site Generator

A bare-bones, Python-based static site generator that converts markdown content into HTML without breaking a sweat (or doing anything fancy). This project was developed as part of [Lane Wagner's Static Site Generator course on Boot.dev](https://www.boot.dev/courses/build-static-site-generator-python), where he describes it as a "Grug-brain" static site generator - because sometimes, the simplest solution is just to bash two rocks together until a website comes out.

## Project Structure

1. `src/` - Core Python source code
2. `content/` - Markdown content files
3. `static/` - Static assets (CSS, images)
4. `template.html` - HTML template for page generation
5. Test files for each component

## Core Components

### 1. Main Engine (`main.py`)
- Entry point that orchestrates the site generation
- Handles directory setup and cleanup
- Manages file copying and page generation

### 2. Markdown Processing (`utils.py`)
- Ultra-basic markdown parsing functionality
- Supports:
  - Headings (H1-H6)
  - Code blocks
  - Blockquotes
  - Ordered and unordered lists
  - Links and images
  - Inline formatting (bold, italic)

### 3. Node System
- `textnode.py` - Base text processing
- `htmlnode.py` - HTML element representation
- `leafnode.py` - Terminal HTML elements
- `parentnode.py` - Container HTML elements

### 4. Template System
- Simple template with `{{ Title }}` and `{{ Content }}` placeholders
- External CSS support

### 5. Content Organization
- Hierarchical content structure in `content/`
- Supports nested directories
- Index-based navigation
- Markdown files with rich formatting

## What Can It Do?
1. Finds markdown files in folders (even nested ones, wow!)
2. Copies your CSS and images without losing them
3. Turns markdown into HTML
4. Uses one template for all pages (why complicate things?)
5. Makes URLs that humans can actually read
6. Has tests (because even Grug knows testing is good)

## Development

### Testing
Tests are located in the `tests/` directory and can be run using:
```bash
./test.sh
```

### Continuous Integration
This project uses GitHub Actions for CI. The workflow:
- Runs on every push to main and pull requests
- Sets up Python 3.10
- Installs dependencies including pytest
- Runs the test suite

You can view the test results in the Actions tab of the GitHub repository.

## Development Practices
I am attempting to follow good Python practices as I learn about them, and I will continue to come back and refine this toy project if I get inspired :smile:
