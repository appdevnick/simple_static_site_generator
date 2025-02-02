import unittest
from textnode import TextNode, TextType
from leafnode import LeafNode
from utils import split_nodes_delimiter

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD_TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD_TEXT)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD_TEXT)
        node2 = TextNode("This is a text node with different text", TextType.BOLD_TEXT)
        self.assertNotEqual(node, node2)

    def test_not_eq_type(self):
        node = TextNode("This is a text node", TextType.BOLD_TEXT)
        node2 = TextNode("This is a text node", TextType.ITALIC_TEXT)
        self.assertNotEqual(node, node2)

    def test_text_node_to_html_node_normal(self):
        node = TextNode("This is a text node", TextType.NORMAL_TEXT)
        html_node = node.text_node_to_html_node()
        self.assertEqual(str(html_node), str(LeafNode(None, "This is a text node", None, None)))

    def test_text_node_to_html_node_bold(self):
        node = TextNode("This is a text node", TextType.BOLD_TEXT)
        html_node = node.text_node_to_html_node()
        self.assertEqual(str(html_node), str(LeafNode("b", "This is a text node", None, None)))

    def test_text_node_to_html_node_italic(self):
        node = TextNode("This is a text node", TextType.ITALIC_TEXT)
        html_node = node.text_node_to_html_node()
        self.assertEqual(str(html_node), str(LeafNode("i", "This is a text node", None, None)))

    def test_text_node_to_html_node_image(self):
        node = TextNode("This is a text node", TextType.IMAGE, url="http://example.com/image.png")
        html_node = node.text_node_to_html_node()
        # Check attributes independently since order doesn't matter
        html_str = str(html_node)
        self.assertIn('alt="This is a text node"', html_str)
        self.assertIn('src="http://example.com/image.png"', html_str)
        self.assertTrue(html_str.startswith('<img') and html_str.endswith('/>'), "Image tag should be self-closing")

    def test_text_node_to_html_node_link(self):
        node = TextNode("This is a text node", TextType.LINK, url="http://example.com")
        html_node = node.text_node_to_html_node()
        self.assertEqual(str(html_node), str(LeafNode("a", "This is a text node", None, {"href": "http://example.com"})))

    def test_text_node_to_html_node_code(self):
        node = TextNode("This is a text node", TextType.CODE)
        html_node = node.text_node_to_html_node()
        self.assertEqual(str(html_node), str(LeafNode("code", "This is a text node", None, None)))

    def test_split_nodes_delimiter_normal(self):
        node = TextNode("This is a `code` node", TextType.NORMAL_TEXT)
        nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_nodes = [
            TextNode("This is a ", TextType.NORMAL_TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" node", TextType.NORMAL_TEXT)
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_split_nodes_delimiter_multiple(self):
        node = TextNode("This is a `code` node with `multiple` delimiters", TextType.NORMAL_TEXT)
        nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_nodes = [
            TextNode("This is a ", TextType.NORMAL_TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" node with ", TextType.NORMAL_TEXT),
            TextNode("multiple", TextType.CODE),
            TextNode(" delimiters", TextType.NORMAL_TEXT)
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("This is a text node without delimiters", TextType.NORMAL_TEXT)
        nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_nodes = [node]
        self.assertEqual(nodes, expected_nodes)

    def test_split_nodes_delimiter_starts_with_delimiter(self):
        node = TextNode("`code` at the start", TextType.NORMAL_TEXT)
        nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_nodes = [
            TextNode("code", TextType.CODE),
            TextNode(" at the start", TextType.NORMAL_TEXT)
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_split_nodes_delimiter_ends_with_delimiter(self):
        node = TextNode("Ends with `code`", TextType.NORMAL_TEXT)
        nodes = split_nodes_delimiter([node], "`", TextType.CODE)        
        expected_nodes = [
            TextNode("Ends with ", TextType.NORMAL_TEXT),
            TextNode("code", TextType.CODE)
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_split_nodes_delimiter_incorrect_number_delimiters(self):
        node = TextNode("This has the wrong *number of asterisk delimiters", TextType.NORMAL_TEXT)
        with self.assertRaises(Exception):
            final_list = split_nodes_delimiter([node], "*", TextType.BOLD_TEXT)

    def test_split_nodes_delimiter_with_multiple_inputs(self):
        node1 = TextNode("There is some `code at the end`", TextType.NORMAL_TEXT)
        node2 = TextNode("`Here is code` at the start", TextType.NORMAL_TEXT)

        nodes = split_nodes_delimiter([node1, node2], "`", TextType.CODE)

        expected_nodes = [
            TextNode("There is some ", TextType.NORMAL_TEXT),
            TextNode("code at the end", TextType.CODE),
            TextNode("Here is code", TextType.CODE),
            TextNode(" at the start", TextType.NORMAL_TEXT)  
        ]

        self.assertEqual(nodes, expected_nodes)
        # return True

if __name__ == "__main__":
    unittest.main()