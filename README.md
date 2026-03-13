## LAB_03 – Advanced Data Structures: Linked Lists, Stacks, and Queues

## Team Members:
- **YADAV Anshuman Krishna** – Exercise 1
- **MAHALINGAM Nithees** – Exercise 2
- **SARAVANAN Arun Prasath** – Exercise 3

---

## Exercise 1 – Social Media Story Feed

A bidirectional content feed implemented using a Doubly Linked List.  
It allows users to seamlessly navigate forward and backward through stories. The algorithm dynamically handles inserting, deleting, and jumping to specific stories without breaking the chain.

It also features a view-tracking system and an in-place Bubble Sort to reorder the entire feed based on story popularity.

### Complexity Summary
- Navigation & Appending: Time O(1), Space O(1)
- Searching/Inserting: Time O(N), Space O(1)
- Sorting by Views: Time O(N²), Space O(1)

---

## Exercise 2 – Activity Feed Processing

A notification and activity management system built using Stacks and Queues.  
It uses a Stack (LIFO) to track recent user activities and a Queue (FIFO) to handle incoming notifications. 

The system includes a priority enqueue feature to push urgent alerts to the front, and a feed processor that can batch-process notifications into the activity history or clear them into an archived log.

### Complexity Summary
- Stack Operations (Push/Pop/Peek): Time O(1)
- Queue Operations (Enqueue/Dequeue): Time O(N) due to Python list shifting, O(1) theoretically for pure queues
- Space: O(N) to store the active items in memory

---

## Exercise 3 – Engagement-Based Priority Queue

A custom priority queue built using a Singly Linked List to rank social media posts.  
Instead of chronological order, posts are assigned a calculated `engagement_score` based on a weighted sum of likes, comments, and shares.

During insertion, the algorithm traverses the linked list to place the new post in its exact sorted position, ensuring the highest engagement content always remains at the top of the feed.

### Complexity Summary
- Insertion: Time O(N) in the worst-case to find the correct sorted position
- Display: Time O(N) to traverse the list
- Space: O(N) to store the post nodes

---

## Overall Reflection

This lab helped us transition from basic collections to sequential and node-based data structures for social networks. We explored:
- Doubly Linked Lists for seamless bidirectional feed navigation
- Stacks (LIFO) for tracking and undoing recent user actions
- Queues (FIFO) for processing notification pipelines
- Priority Queues (via Linked Lists) for algorithmically ranking content feeds

By building these from scratch, we gained a practical understanding of pointer manipulation and the distinct algorithmic trade-offs of sequential processing. We saw firsthand how choosing between a Stack, Queue, or Priority Queue directly dictates the user experience of a social media platform.