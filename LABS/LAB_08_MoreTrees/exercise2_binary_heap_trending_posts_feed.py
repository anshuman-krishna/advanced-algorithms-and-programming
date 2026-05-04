import time
import math

class TrendingHeap:
    def __init__(self):
        self.heap = []
        self.position = {}
    def parent(self, i):
        return (i - 1) // 2
    def left(self, i):
        return 2 * i + 1
    def right(self, i):
        return 2 * i + 2
    def swap(self, i, j):
        self.position[self.heap[i][1]] = j
        self.position[self.heap[j][1]] = i
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    def heapify_up(self, i):
        while i > 0:
            p = self.parent(i)
            if self.heap[i][0] > self.heap[p][0]:
                self.swap(i, p)
                i = p
            else:
                break
    def heapify_down(self, i):
        n = len(self.heap)
        while True:
            largest = i
            l = self.left(i)
            r = self.right(i)

            if l < n and self.heap[l][0] > self.heap[largest][0]:
                largest = l

            if r < n and self.heap[r][0] > self.heap[largest][0]:
                largest = r

            if largest != i:
                self.swap(i, largest)
                i = largest
            else:
                break
    def push(self, post_id, likes, timestamp):
        node = [likes, post_id, timestamp]
        self.heap.append(node)
        index = len(self.heap) - 1
        self.position[post_id] = index
        self.heapify_up(index)
    def pop_max(self):
        if not self.heap:
            return None
        max_post = self.heap[0]
        last = self.heap.pop()
        if self.heap:
            self.heap[0] = last
            self.position[last[1]] = 0
            self.heapify_down(0)
        del self.position[max_post[1]]
        return max_post
    def peek_max(self):
        return self.heap[0] if self.heap else None
    def update_likes(self, post_id, new_likes):
        if post_id not in self.position:
            print("Post ID not found!")
            return
        i = self.position[post_id]
        old_likes = self.heap[i][0]
        self.heap[i][0] = new_likes
        self.heap[i][2] = time.time()
        if new_likes > old_likes:
            self.heapify_up(i)
        else:
            self.heapify_down(i)
    def get_top_k(self, k):
        temp = TrendingHeap()
        for node in self.heap:
            temp.push(node[1], node[0], node[2])
        result = []
        for _ in range(min(k, len(self.heap))):
            result.append(temp.pop_max())
        return result
    def size(self):
        return len(self.heap)
    def get_height(self):
        if len(self.heap) == 0:
            return 0
        return math.floor(math.log2(len(self.heap)))
    def is_valid_heap(self, i=0):
        n = len(self.heap)
        l = self.left(i)
        r = self.right(i)
        if l < n and self.heap[l][0] > self.heap[i][0]:
            return False
        if r < n and self.heap[r][0] > self.heap[i][0]:
            return False
        left_valid = True
        right_valid = True
        if l < n:
            left_valid = self.is_valid_heap(l)
        if r < n:
            right_valid = self.is_valid_heap(r)
        return left_valid and right_valid
    def display(self):
        print("\nHeap (Level Order):")
        for node in self.heap:
            print(f"PostID: {node[1]}, Likes: {node[0]}")

heap = TrendingHeap()
while True:
    print("\n===== Trending Posts Menu =====")
    print("1. Add Post")
    print("2. Update Likes")
    print("3. View Top Post")
    print("4. Remove Top Post")
    print("5. Get Top K Posts")
    print("6. Heap Size")
    print("7. Heap Height")
    print("8. Validate Heap")
    print("9. Display Heap")
    print("0. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        post_id = int(input("Enter Post ID: "))
        likes = int(input("Enter Likes: "))
        heap.push(post_id, likes, time.time())
        print("Post added!")
    elif choice == "2":
        post_id = int(input("Enter Post ID: "))
        new_likes = int(input("Enter New Likes: "))
        heap.update_likes(post_id, new_likes)
    elif choice == "3":
        print("Top Post:", heap.peek_max())
    elif choice == "4":
        print("Removed:", heap.pop_max())
    elif choice == "5":
        k = int(input("Enter K: "))
        top_posts = heap.get_top_k(k)
        print("Top Posts:")
        for post in top_posts:
            print(post)
    elif choice == "6":
        print("Heap Size:", heap.size())
    elif choice == "7":
        print("Heap Height:", heap.get_height())
    elif choice == "8":
        print("Valid Heap:", heap.is_valid_heap())
    elif choice == "9":
        heap.display()
    elif choice == "0":
        print("Exiting...")
        break
    else:
        print("Invalid choice! Try again.")