class Post:
    def __init__(self, post_id, user_id, content, timestamp, likes, comments, shares):
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.timestamp = timestamp
        self.likes = likes
        self.comments = comments
        self.shares = shares
        self.engagement_score = (likes * 1) + (comments * 2) + (shares * 3)
        self.next = None


class PriorityQueue:
    def __init__(self):
        self.head = None

    def insert_post(self, new_post):
        if self.head is None or new_post.engagement_score > self.head.engagement_score:
            new_post.next = self.head
            self.head = new_post
        else:
            current = self.head
            while current.next is not None and current.next.engagement_score >= new_post.engagement_score:
                current = current.next

            new_post.next = current.next
            current.next = new_post

    def display_posts(self):
        current = self.head
        while current:
            print("Post ID:", current.post_id)
            print("Content:", current.content)
            print("Score:", current.engagement_score)
            print("---------------------")
            current = current.next


pq = PriorityQueue()

post1 = Post(1, 101, "Hello World", "13-03-2026", 10, 5, 2)
post2 = Post(2, 102, "Good Morning", "13-03-2026", 5, 2, 1)
post3 = Post(3, 103, "Python is fun", "13-03-2026", 20, 10, 5)

pq.insert_post(post1)
pq.insert_post(post2)
pq.insert_post(post3)

pq.display_posts()