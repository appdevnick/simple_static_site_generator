import unittest
from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        props = {
            "href": "https://www.google.com",
            "target": "_blank",
        }

        node = HTMLNode("a", "anchor text", None, props)

        self.assertEqual(node.props_to_html(), f"\"href\"=https://www.google.com \"target\"=_blank")

if __name__ == "__main__":
    unittest.main()