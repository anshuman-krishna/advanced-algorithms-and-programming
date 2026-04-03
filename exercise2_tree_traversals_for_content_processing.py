class Node:
    def __init__(self, name, posts=0):
        self.name = name
        self.posts = posts
        self.children = []
        self.total_posts = 0

def build_tree():
    name = input("Enter node name: ")
    posts = int(input(f"Enter posts for {name}: "))
    node = Node(name, posts)
    num_children = int(input(f"Enter number of children for {name}: "))
    for i in range(num_children):
        print(f"\nEntering child {i+1} of {name}")
        child = build_tree()
        node.children.append(child)
    return node

def in_order(node):
    if not node:
        return []
    result = []
    n = len(node.children)
    mid = n // 2
    for i in range(mid):
        result += in_order(node.children[i])
    result.append(node.name)
    for i in range(mid, n):
        result += in_order(node.children[i])
    return result

def in_order_accumulate(node):
    if not node:
        return 0
    total = 0
    n = len(node.children)
    mid = n // 2
    for i in range(mid):
        total += in_order_accumulate(node.children[i])
    total += node.posts
    for i in range(mid, n):
        total += in_order_accumulate(node.children[i])
    return total

def pre_order(node):
    if not node:
        return []
    result = [node.name]
    for child in node.children:
        result += pre_order(child)
    return result

def post_order_total_posts(node):
    if not node:
        return 0
    total = node.posts
    for child in node.children:
        total += post_order_total_posts(child)
    node.total_posts = total
    return total

def collect_leaves(node):
    if not node:
        return []
    if not node.children:
        return [node.name]
    leaves = []
    for child in node.children:
        leaves += collect_leaves(child)
    return leaves

def most_popular(node):
    if not node:
        return (None, float("-inf"))
    if not node.children:
        return (node.name, node.posts)
    best_name, best_posts = None, float("-inf")
    for child in node.children:
        name, posts = most_popular(child)
        if posts > best_posts:
            best_name, best_posts = name, posts
    return best_name, best_posts

print("Build Your Tree")
root = build_tree()
print("\n--- RESULTS ---")
print("In-order Traversal:", in_order(root))
print("Pre-order Traversal:", pre_order(root))
print("Total Posts (In-order Accumulate):", in_order_accumulate(root))
print("Total Posts (Post-order):", post_order_total_posts(root))
print("Leaf Nodes:", collect_leaves(root))
print("Most Popular Category:", most_popular(root))