from textnode import TextNode, TextType

def main():
    test_node = TextNode("`This is a text` node with 2 `code blocks` in it", TextType.NORMAL_TEXT)
    res = test_node.split_nodes_delimiter([test_node], "`", TextType.CODE)
    print(res)

main()