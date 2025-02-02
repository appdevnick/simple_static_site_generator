import unittest
from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_eq(self):
        props = {
            "href": "https://www.google.com",
            "target": "_blank",
        }

        node = LeafNode("a", "anchor text", None, props)

        self.assertEqual(node.to_html(), f"<a href=\"https://www.google.com\" target=\"_blank\">anchor text</a>")

if __name__ == "__main__":
    unittest.main()