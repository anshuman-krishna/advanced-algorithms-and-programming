from collections import deque

class GeneralizedNode:
    def __init__(self, category_id, name, post_count=0):
        self.category_id = category_id
        self.name = name
        self.post_count = post_count
        self.children = []
        self.parent = None


class BinaryNode:
    def __init__(self, category_id, name):
        self.category_id = category_id
        self.name = name
        self.left = None
        self.right = None


def binary_to_generalized(binary_node, parent=None):
    if binary_node is None:
        return None
    new_node = GeneralizedNode(binary_node.category_id, binary_node.name)
    new_node.parent = parent
    child = binary_node.left
    while child:
        converted_child = binary_to_generalized(child, new_node)
        new_node.children.append(converted_child)
        child = child.right
    return new_node


def generalized_to_binary(gen_node):
    if gen_node is None:
        return None
    binary_node = BinaryNode(gen_node.category_id, gen_node.name)
    if gen_node.children:
        binary_node.left = generalized_to_binary(gen_node.children[0])
        current = binary_node.left
        for child in gen_node.children[1:]:
            current.right = generalized_to_binary(child)
            current = current.right
    return binary_node


def pre_order_generalized(node):
    if node is None:
        return
    print(node.name, end=" ")
    for child in node.children:
        pre_order_generalized(child)


def post_order_generalized(node):
    if node is None:
        return
    for child in node.children:
        post_order_generalized(child)
    print(node.name, end=" ")


def level_order_generalized(root):
    if root is None:
        return
    queue = deque([root])
    while queue:
        current = queue.popleft()
        print(current.name, end=" ")
        for child in current.children:
            queue.append(child)


def calculate_height(node):
    if node is None:
        return 0
    if not node.children:
        return 1
    return 1 + max(calculate_height(child) for child in node.children)


def count_nodes(node):
    if node is None:
        return 0
    total = 1
    for child in node.children:
        total += count_nodes(child)
    return total


def count_leaves(node):
    if node is None:
        return 0
    if not node.children:
        return 1
    total = 0
    for child in node.children:
        total += count_leaves(child)
    return total


def calculate_fan_out(node):
    if node is None:
        return 0
    max_children = len(node.children)
    for child in node.children:
        max_children = max(max_children, calculate_fan_out(child))
    return max_children


def calculate_branching_factor(root):
    total_children = 0
    non_leaf_nodes = 0
    def helper(node):
        nonlocal total_children, non_leaf_nodes
        if node is None:
            return
        if node.children:
            total_children += len(node.children)
            non_leaf_nodes += 1
        for child in node.children:
            helper(child)
    helper(root)
    return total_children / non_leaf_nodes if non_leaf_nodes != 0 else 0


if __name__ == "__main__":
    root = GeneralizedNode(1, "A")
    b = GeneralizedNode(2, "B")
    c = GeneralizedNode(3, "C")
    d = GeneralizedNode(4, "D")

    root.children = [b, c, d]

    b.children = [GeneralizedNode(5, "E"), GeneralizedNode(6, "F")]
    c.children = [GeneralizedNode(7, "G")]

    print("Pre-order:")
    pre_order_generalized(root)

    print("\nPost-order:")
    post_order_generalized(root)

    print("\nLevel-order:")
    level_order_generalized(root)

    print("\n\nHeight:", calculate_height(root))
    print("Total Nodes:", count_nodes(root))
    print("Leaf Nodes:", count_leaves(root))
    print("Max Fan-out:", calculate_fan_out(root))
    print("Branching Factor:", calculate_branching_factor(root))