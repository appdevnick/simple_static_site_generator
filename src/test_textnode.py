import unittest
from textnode import TextNode, TextType
from leafnode import LeafNode

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
        self.assertEqual(str(html_node), str(LeafNode("img", "", None, {"src": "http://example.com/image.png", "alt": "This is a text node"})))

    def test_text_node_to_html_node_link(self):
        node = TextNode("This is a text node", TextType.LINK, url="http://example.com")
        html_node = node.text_node_to_html_node()
        self.assertEqual(str(html_node), str(LeafNode("a", "This is a text node", None, {"href": "http://example.com"})))

    def test_text_node_to_html_node_code(self):
        node = TextNode("This is a text node", TextType.CODE)
        html_node = node.text_node_to_html_node()
        self.assertEqual(str(html_node), str(LeafNode("code", "This is a text node", None, None)))

if __name__ == "__main__":
    unittest.main()