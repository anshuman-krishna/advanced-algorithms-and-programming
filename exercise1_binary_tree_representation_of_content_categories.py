class CategoryNode:
    def __init__(self, category_id, name, post_count):
        self.category_id = category_id
        self.name = name
        self.post_count = post_count
        self.left = None
        self.right = None
        self.parent = None

def calculate_height(node):
    if node is None:
        return 0
    left_height = calculate_height(node.left)
    right_height = calculate_height(node.right)
    return max(left_height, right_height) + 1

def find_category(category_id, node):
    if node is None:
        return None
    if node.category_id == category_id:
        return node
    
    left_search = find_category(category_id, node.left)
    if left_search is not None:
        return left_search
        
    return find_category(category_id, node.right)

def calculate_node_height(node, target_id):
    target_node = find_category(target_id, node)
    if target_node is None:
        return 0
    return calculate_height(target_node)

def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

def count_leaves(node):
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return 1
    return count_leaves(node.left) + count_leaves(node.right)

def is_balanced(node):
    if node is None:
        return True
    left_h = calculate_height(node.left)
    right_h = calculate_height(node.right)
    diff = abs(left_h - right_h)
    
    if diff <= 1 and is_balanced(node.left) and is_balanced(node.right):
        return True
    return False

def is_full_binary_tree(node):
    if node is None:
        return True
    if node.left is None and node.right is None:
        return True
    if node.left is not None and node.right is not None:
        return is_full_binary_tree(node.left) and is_full_binary_tree(node.right)
    return False

def is_perfect_binary_tree(node):
    if is_full_binary_tree(node) and is_balanced(node):
        return True
    return False

def is_complete_binary_tree(node):
    if node is None:
        return True
    
    queue = []
    queue.append(node)
    flag = False
    
    while len(queue) > 0:
        current = queue.pop(0)
        
        if current is None:
            flag = True
        else:
            if flag is True:
                return False
            queue.append(current.left)
            queue.append(current.right)
            
    return True

def find_path_to_root(category_id, node):
    target = find_category(category_id, node)
    path = []
    
    while target is not None:
        path.append(target.name)
        target = target.parent
        
    return path

def lowest_common_ancestor(id1, id2, node):
    if node is None:
        return None
        
    if node.category_id == id1 or node.category_id == id2:
        return node
        
    left_lca = lowest_common_ancestor(id1, id2, node.left)
    right_lca = lowest_common_ancestor(id1, id2, node.right)
    
    if left_lca is not None and right_lca is not None:
        return node
        
    if left_lca is not None:
        return left_lca
        
    return right_lca

# verification via testing
if __name__ == "__main__":
    root = CategoryNode("1", "Technology", 500)
    
    hw = CategoryNode("2", "Hardware", 200)
    sw = CategoryNode("3", "Software", 300)
    hw.parent = root
    sw.parent = root
    root.left = hw
    root.right = sw
    
    laptops = CategoryNode("4", "Laptops", 150)
    phones = CategoryNode("5", "Phones", 50)
    laptops.parent = hw
    phones.parent = hw
    hw.left = laptops
    hw.right = phones
    
    os = CategoryNode("6", "Operating Systems", 100)
    apps = CategoryNode("7", "Applications", 200)
    os.parent = sw
    apps.parent = sw
    sw.left = os
    sw.right = apps

    print("Binary Tree Verification:")
    print(f"Total Nodes: {count_nodes(root)}")
    print(f"Total Leaves: {count_leaves(root)}")
    print(f"Tree Height: {calculate_height(root)}")
    
    print("\nTree Properties:")
    print(f"Is Full Binary Tree? {is_full_binary_tree(root)}")
    print(f"Is Balanced? {is_balanced(root)}")
    print(f"Is Perfect Binary Tree? {is_perfect_binary_tree(root)}")
    print(f"Is Complete Binary Tree? {is_complete_binary_tree(root)}")
    
    print("\nNavigation and Search:")
    path = find_path_to_root("4", root)
    print(f"Path from Laptops to root: {path}")
    
    lca = lowest_common_ancestor("4", "5", root)
    print(f"Lowest Common Ancestor of Laptops and Phones: {lca.name}")
    
    lca_cross = lowest_common_ancestor("4", "7", root)
    print(f"Lowest Common Ancestor of Laptops and Apps: {lca_cross.name}")