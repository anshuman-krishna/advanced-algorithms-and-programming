class UserBST:
    def __init__(self, user_id, name, friends):
        self.user_id = user_id
        self.name = name
        self.friends = friends
        self.left = None
        self.right = None

def insert(root, user_id, name, friends_list):
    if root is None:
        return UserBST(user_id, name, friends_list)
    if user_id < root.user_id:
        root.left = insert(root.left, user_id, name, friends_list)
    elif user_id > root.user_id:
        root.right = insert(root.right, user_id, name, friends_list)
    return root

def find(root, target_id):
    if root is None or root.user_id == target_id:
        return root
    if target_id < root.user_id:
        return find(root.left, target_id)
    return find(root.right, target_id)

def inorder_traversal(root):
    result = []
    if root is None:
        return result
    result.extend(inorder_traversal(root.left))
    result.append(root.user_id)
    result.extend(inorder_traversal(root.right))
    return result

def find_min(node):
    current = node
    while current.left is not None:
        current = current.left
    return current

def delete(root, target_id):
    if root is None:
        return root
    if target_id < root.user_id:
        root.left = delete(root.left, target_id)
    elif target_id > root.user_id:
        root.right = delete(root.right, target_id)
    else:
        if root.left is None:
            return root.right
        elif root.right is None:
            return root.left
        min_node = find_min(root.right)
        root.user_id = min_node.user_id
        root.name = min_node.name
        root.friends = min_node.friends
        root.right = delete(root.right, min_node.user_id)
    return root

def suggest_friends(root, target_id, max_suggestions):
    target_user = find(root, target_id)
    if target_user is None:
        return []
    
    fof_counts = {}
    for friend_id in target_user.friends:
        friend_node = find(root, friend_id)
        if friend_node is not None:
            for fof_id in friend_node.friends:
                if fof_id != target_id and fof_id not in target_user.friends:
                    if fof_id in fof_counts:
                        fof_counts[fof_id] += 1
                    else:
                        fof_counts[fof_id] = 1
                        
    sorted_fofs = sorted(fof_counts.items(), key=lambda item: item[1], reverse=True)
    return [fof[0] for fof in sorted_fofs[:max_suggestions]]

def get_height(root):
    if root is None:
        return 0
    left_h = get_height(root.left)
    right_h = get_height(root.right)
    return max(left_h, right_h) + 1

def is_balanced(root):
    if root is None:
        return True
    left_h = get_height(root.left)
    right_h = get_height(root.right)
    diff = abs(left_h - right_h)
    if diff <= 1 and is_balanced(root.left) and is_balanced(root.right):
        return True
    return False

def get_leaf_count(root):
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    return get_leaf_count(root.left) + get_leaf_count(root.right)


# verification
if __name__ == "__main__":
    print("Initializing User BST")
    root = None
    root = insert(root, 50, "Alice", [30, 70, 20])
    root = insert(root, 30, "Bob", [50, 20, 40])
    root = insert(root, 70, "Charlie", [50, 60, 80])
    root = insert(root, 20, "David", [30, 50])
    root = insert(root, 40, "Eve", [30, 60])
    root = insert(root, 60, "Frank", [70, 40])
    root = insert(root, 80, "Grace", [70])

    print("\nTesting Traversals & Search:")
    print(f"Inorder IDs (Should be sorted): {inorder_traversal(root)}")
    found_user = find(root, 40)
    print(f"Searched for ID 40: Found {found_user.name} with friends {found_user.friends}")

    print("\nTesting Friend Suggestions:")
    suggestions = suggest_friends(root, 20, 2)
    print(f"Friend suggestions for David (ID 20): {suggestions}")

    print("\nTesting Tree Metrics:")
    print(f"Tree Height: {get_height(root)}")
    print(f"Leaf Count: {get_leaf_count(root)}")
    print(f"Is tree balanced? {is_balanced(root)}")

    print("\nTesting Deletion:")
    root = delete(root, 30)
    print(f"Inorder IDs after deleting Bob (ID 30): {inorder_traversal(root)}")