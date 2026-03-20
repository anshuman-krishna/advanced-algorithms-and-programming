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

def max_engagement(posts, left, right):
    if left == right:
        return posts[left]
    mid = (left + right) // 2
    left_max = max_engagement(posts, left, mid)
    right_max = max_engagement(posts, mid + 1, right)
    return left_max if left_max.engagement_score > right_max.engagement_score else right_max

def sum_engagement(posts, left, right):
    if left == right:
        return posts[left].engagement_score
    mid = (left + right) // 2
    return sum_engagement(posts, left, mid) + sum_engagement(posts, mid + 1, right)

def average_engagement(posts, left, right):
    total = sum_engagement(posts, left, right)
    n = right - left + 1
    return total / n

def count_above_threshold(posts, left, right, threshold):
    if left == right:
        return 1 if posts[left].engagement_score > threshold else 0
    mid = (left + right) // 2
    return (count_above_threshold(posts, left, mid, threshold) +
            count_above_threshold(posts, mid + 1, right, threshold))

def merge(posts, left, mid, right):
    L = posts[left:mid+1]
    R = posts[mid+1:right+1]
    i = j = 0
    k = left
    while i < len(L) and j < len(R):
        if L[i].engagement_score <= R[j].engagement_score:
            posts[k] = L[i]
            i += 1
        else:
            posts[k] = R[j]
            j += 1
        k += 1
    while i < len(L):
        posts[k] = L[i]
        i += 1
        k += 1
    while j < len(R):
        posts[k] = R[j]
        j += 1
        k += 1

def merge_sort(posts, left, right):
    if left < right:
        mid = (left + right) // 2
        merge_sort(posts, left, mid)
        merge_sort(posts, mid + 1, right)
        merge(posts, left, mid, right)

def find_peak_hour(likes, left, right):
    if left == right:
        return left
    mid = (left + right) // 2
    if likes[mid] < likes[mid + 1]:
        return find_peak_hour(likes, mid + 1, right)
    else:
        return find_peak_hour(likes, left, mid)

posts = []
n = int(input("Enter number of posts: "))
for i in range(n):
    print(f"\nEnter details for Post {i+1}")
    post_id = int(input("Post ID: "))
    user_id = int(input("User ID: "))
    content = input("Content: ")
    timestamp = input("Timestamp: ")
    likes = int(input("Likes: "))
    comments = int(input("Comments: "))
    shares = int(input("Shares: "))
    posts.append(Post(post_id, user_id, content, timestamp, likes, comments, shares))

if len(posts) > 0:
    max_post = max_engagement(posts, 0, len(posts)-1)
    print("\nMax Engagement:", max_post.post_id, max_post.engagement_score)
    print("Total Engagement:", sum_engagement(posts, 0, len(posts)-1))
    print("Average Engagement:", average_engagement(posts, 0, len(posts)-1))
    threshold = int(input("\nEnter threshold: "))
    print("Above Threshold:", count_above_threshold(posts, 0, len(posts)-1, threshold))
    merge_sort(posts, 0, len(posts)-1)
    print("Sorted Engagement:", [p.engagement_score for p in posts])
else:
    print("No posts available")

print("\n--- Peak Hour ---")
h = int(input("Enter number of hours: "))
likes = []
for i in range(h):
    likes.append(int(input(f"Likes at hour {i}: ")))
if len(likes) > 0:
    peak = find_peak_hour(likes, 0, len(likes)-1)
    print("Peak Hour Index:", peak, "Likes:", likes[peak])
else:
    print("No data")