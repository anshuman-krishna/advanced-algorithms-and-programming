class CommentNode:
    def __init__(self, comment_id, user_id, content, timestamp, likes):
        self.comment_id = comment_id
        self.user_id = user_id
        self.content = content
        self.timestamp = timestamp
        self.likes = likes
        self.replies = []

def display_thread(comment, level=0):
    indentation = "  " * level
    print(indentation + comment.content)
    for reply in comment.replies:
        display_thread(reply, level + 1)

def count_total_comments(comment):
    total = 1
    for reply in comment.replies:
        total += count_total_comments(reply)
    return total

def total_likes(comment):
    sum_likes = comment.likes
    for reply in comment.replies:
        sum_likes += total_likes(reply)
    return sum_likes

def find_deepest_reply(comment):
    max_depth = 0
    for reply in comment.replies:
        depth = find_deepest_reply(reply)
        if depth > max_depth:
            max_depth = depth
    return max_depth + 1

def search_by_user(user_id, comment):
    results = []
    if comment.user_id == user_id:
        results.append(comment)
    for reply in comment.replies:
        child_results = search_by_user(user_id, reply)
        results.extend(child_results)
    return results

def contains_keyword(keyword, comment):
    if keyword in comment.content:
        return True
    for reply in comment.replies:
        if contains_keyword(keyword, reply):
            return True
    return False

def delete_comment(comment_id, thread):
    if thread.comment_id == comment_id:
        return None
    
    new_replies = []
    for reply in thread.replies:
        filtered_reply = delete_comment(comment_id, reply)
        if filtered_reply is not None:
            new_replies.append(filtered_reply)
    
    thread.replies = new_replies
    return thread


# verification
if __name__ == "__main__":
    root = CommentNode("1", "userA", "This is the original post example!", 1000, 50)
    
    reply1 = CommentNode("2", "userB", "What do you think about recursion?", 1005, 10)
    reply2 = CommentNode("3", "userC", "Not sure about this.", 1010, 5)
    
    reply1_1 = CommentNode("4", "userA", "I hope it doesn't appear in the exam!", 1015, 20)
    reply1_1_1 = CommentNode("5", "userD", "Recursion is quite difficult.", 1020, 100)
    
    reply1.replies.append(reply1_1)
    reply1_1.replies.append(reply1_1_1)
    root.replies.extend([reply1, reply2])
    
    print("--- displaying Thread ---")
    display_thread(root)
    
    print("\n--- thread Metrics ---")
    print(f"Total Comments: {count_total_comments(root)}")
    print(f"Total Likes: {total_likes(root)}")
    print(f"Max Depth: {find_deepest_reply(root)}")
    
    print("\n--- searching ---")
    print(f"Contains 'cool'? {contains_keyword('cool', root)}")
    
    userA_comments = search_by_user("userA", root)
    print(f"Comments by userA: {len(userA_comments)}")
    
    print("\n--- deletion ---")
    root = delete_comment("2", root)
    print("thread after deleting comment '2' (should cascade remove 4 and 5):")
    display_thread(root)