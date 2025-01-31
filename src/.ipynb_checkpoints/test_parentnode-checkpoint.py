import unittest
from parentnode import ParentNode
from leafnode import LeafNode
from textnode import TextNode

class TestParentNode(unittest.TestCase):
    def test_to_html_with_valid_data(self):
        child1 = LeafNode("p", "Child 1", None, None)
        child2 = LeafNode("p", "Child 2", None, None)
        parent = ParentNode("div", [child1, child2], {"class": "container"})
        expected_html = '<div class="container"><p>Child 1</p><p>Child 2</p></div>'
        self.assertEqual(parent.to_html(), expected_html)

    def test_to_html_no_tag(self):
        with self.assertRaises(ValueError) as context:
            ParentNode("", [LeafNode("p", "Child", None, None)]).to_html()
        self.assertEqual(str(context.exception), "No tag provided to a ParentNode")

    def test_to_html_no_children(self):
        with self.assertRaises(ValueError) as context:
            ParentNode("div", []).to_html()
        self.assertEqual(str(context.exception), "No children provided to a ParentNode")

    def test_nested_parents(self):
        node_tree = ParentNode("div", [
            ParentNode("div", [
                LeafNode("b", "this is a bold paragraph in a leaf node", None, {"data-id": "69"})
            ])
        ], {"class": "blue-border"})

        self.assertEqual(node_tree.to_html(), "<div class=\"blue-border\"><div><b data-id=\"69\">this is a bold paragraph in a leaf node</b></div></div>")

    

if __name__ == "__main__":
    unittest.main()