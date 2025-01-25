# Documentation

## HTMLNode Class

### `__init__(self, tag: str=None, value: str=None, children: List=None, props: dict=None)`
Initializes an HTMLNode object.

- **Parameters:**
  - `tag` (str): The HTML tag for the node.
  - `value` (str): The value or content of the node.
  - `children` (List): A list of child nodes.
  - `props` (dict): A dictionary of properties for the node.

### `to_html(self)`
Raises a NotImplementedError. This method should be implemented by subclasses.

### `props_to_html(self)`
Converts the properties dictionary to an HTML string.

- **Returns:**
  - `str`: A string representation of the properties.

## LeafNode Class

### `__init__(self, tag: str, value: str, children: List, props: dict)`
Initializes a LeafNode object.

- **Parameters:**
  - `tag` (str): The HTML tag for the node.
  - `value` (str): The value or content of the node.
  - `children` (List): A list of child nodes (should be None for LeafNode).
  - `props` (dict): A dictionary of properties for the node.

### `__repr__(self)`
Returns a string representation of the LeafNode object.

- **Returns:**
  - `str`: A string representation of the LeafNode.

### `to_html(self)`
Converts the LeafNode to an HTML string.

- **Returns:**
  - `str`: An HTML string representation of the LeafNode.

## ParentNode Class

### `__init__(self, tag: str, children: List, props: dict = None)`
Initializes a ParentNode object.

- **Parameters:**
  - `tag` (str): The HTML tag for the node.
  - `children` (List): A list of child nodes.
  - `props` (dict): A dictionary of properties for the node.

### `to_html(self)`
Converts the ParentNode and its children to an HTML string.

- **Returns:**
  - `str`: An HTML string representation of the ParentNode.

## TextNode Class

### `__init__(self, text: str, text_type: TextType, url: str=None)`
Initializes a TextNode object.

- **Parameters:**
  - `text` (str): The text content of the node.
  - `text_type` (TextType): The type of text (e.g., normal, bold, italic).
  - `url` (str): The URL for link or image nodes.

### `__eq__(self, other)`
Checks if two TextNode objects are equal.

- **Parameters:**
  - `other` (TextNode): Another TextNode object.

- **Returns:**
  - `bool`: True if the nodes are equal, False otherwise.

### `__repr__(self)`
Returns a string representation of the TextNode object.

- **Returns:**
  - `str`: A string representation of the TextNode.

### `text_node_to_html_node(self)`
Converts the TextNode to an HTML node.

- **Returns:**
  - `LeafNode`: An HTML node representation of the TextNode.

## Utility Functions

### `split_nodes_delimiter(old_nodes: List, delimiter, text_type)`
Splits text nodes by a delimiter and assigns a new text type to the delimited text.

- **Parameters:**
  - `old_nodes` (List): A list of TextNode objects.
  - `delimiter` (str): The delimiter to split the text.
  - `text_type` (TextType): The new text type for the delimited text.

- **Returns:**
  - `List`: A list of TextNode objects.

### `extract_markdown_images(text)`
Extracts image markdown from text.

- **Parameters:**
  - `text` (str): The input text containing markdown images.

- **Returns:**
  - `List`: A list of tuples containing image alt text and URLs.

### `extract_markdown_links(text)`
Extracts link markdown from text.

- **Parameters:**
  - `text` (str): The input text containing markdown links.

- **Returns:**
  - `List`: A list of tuples containing link text and URLs.

### `split_nodes_image(old_nodes)`
Splits text nodes containing markdown images into separate nodes.

- **Parameters:**
  - `old_nodes` (List): A list of TextNode objects.

- **Returns:**
  - `List`: A list of TextNode objects.

### `split_nodes_link(old_nodes)`
Splits text nodes containing markdown links into separate nodes.

- **Parameters:**
  - `old_nodes` (List): A list of TextNode objects.

- **Returns:**
  - `List`: A list of TextNode objects.

### `text_to_textnodes(text)`
Converts a text string to a list of TextNode objects, handling markdown formatting.

- **Parameters:**
  - `text` (str): The input text.

- **Returns:**
  - `List`: A list of TextNode objects.

### `markdown_to_blocks(markdown)`
Splits markdown content into blocks based on blank lines.

- **Parameters:**
  - `markdown` (str): The input markdown content.

- **Returns:**
  - `List`: A list of markdown blocks.

### `block_to_block_type(markdown_block)`
Determines the type of a markdown block.

- **Parameters:**
  - `markdown_block` (str): A block of markdown content.

- **Returns:**
  - `str`: The type of the markdown block (e.g., heading, code, quote).

### `head_level(heading)`
Determines the level of a markdown heading.

- **Parameters:**
  - `heading` (str): A markdown heading.

- **Returns:**
  - `int`: The level of the heading.

### `text_to_children(text_block)`
Converts a text block to a list of child nodes.

- **Parameters:**
  - `text_block` (str): A block of text.

- **Returns:**
  - `List`: A list of child nodes.

### `lstrip_n(string, char, n)`
Strips up to `n` occurrences of a character from the start of a string.

- **Parameters:**
  - `string` (str): The input string.
  - `char` (str): The character to strip.
  - `n` (int): The maximum number of characters to strip.

- **Returns:**
  - `str`: The modified string.

### `markdown_to_html_node(markdown)`
Converts markdown content to an HTMLNode object.

- **Parameters:**
  - `markdown` (str): The input markdown content.

- **Returns:**
  - `HTMLNode`: An HTMLNode object representing the markdown content.