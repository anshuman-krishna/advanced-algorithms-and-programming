class Comment:
    def __init__(self, text):
        self.text = text
        self.replies = []

    def add_reply(self, reply):
        self.replies.append(reply)


def flatten_recursive(comment):
    result = [comment]
    for reply in comment.replies:
        result += flatten_recursive(reply)
    return result


def flatten_iterative(comment):
    stack = [(comment, "START")]
    result = []

    while stack:
        node, state = stack.pop()
        if state == "START":
            result.append(node)
            stack.append((node, "DONE"))
            for reply in reversed(node.replies):
                stack.append((reply, "START"))

    return result


def count_comments_tail(comment, count=0):
    count += 1
    for reply in comment.replies:
        count = count_comments_tail(reply, count)
    return count


def count_comments_loop(comment):
    stack = [comment]
    count = 0

    while stack:
        node = stack.pop()
        count += 1
        for reply in node.replies:
            stack.append(reply)

    return count


root = Comment("Main Comment")

reply1 = Comment("Reply 1")
reply2 = Comment("Reply 2")
reply3 = Comment("Reply 3")

sub_reply1 = Comment("Reply 1.1")
sub_reply2 = Comment("Reply 1.2")

reply1.add_reply(sub_reply1)
reply1.add_reply(sub_reply2)

root.add_reply(reply1)
root.add_reply(reply2)
root.add_reply(reply3)


flat_list_recursive = flatten_recursive(root)
for c in flat_list_recursive:
    print(c.text)

flat_list_iterative = flatten_iterative(root)
for c in flat_list_iterative:
    print(c.text)

print(count_comments_tail(root))
print(count_comments_loop(root))