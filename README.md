# Advanced Algorithms and Programming

## Team Members & Contributions
* **YADAV Anshuman Krishna**
  * Lab 1: Exercises 4, 5, 6
  * Lab 2: Exercises 2, 4
  * Lab 3: Exercise 1
  * Lab 4: Exercise 1
  * Lab 5: Exercise 1 & Final Integration
* **MAHALINGAM Nithees**
  * Lab 1: Exercises 1, 2, 3
  * Lab 2: Exercise 1
  * Lab 3: Exercise 2
  * Lab 4: Exercise 2
  * Lab 5: Exercise 2
* **SARAVANAN Arun Prasath**
  * Lab 1: Absent
  * Lab 2: Exercise 3
  * Lab 3: Exercise 3
  * Lab 4: Exercise 3
  * Lab 5: Exercise 3

---

## LAB 01: Revision of Algorithms Fundamentals

### Exercise 1: Integer Mirror
We reversed an integer mathematically (`%`, `//`, `*`) without taking the easy route of converting it to a string.
* **Complexity:** Time O(d) where d is digits, Space O(1)

### Exercise 2: Balanced Symbol Checker
We used a stack to check if brackets in a string are perfectly balanced. We pushed opening brackets onto the stack and popped them when finding a match, returning false if things did not line up.
* **Complexity:** Time O(n), Space O(n)

### Exercise 3: Merge Overlapping Intervals
We sorted intervals by their start times and merged them in a single pass using the `max` function to handle overlapping ends.
* **Complexity:** Time O(n log n), Space O(n)

### Exercise 4: Polynomial Evaluation
We applied Horner's Method to evaluate polynomials iteratively, which drastically cut down on unnecessary mathematical multiplications.
* **Complexity:** Time O(n), Space O(1)

### Exercise 5: Array Rotation Optimization
We tested three rotation methods (temporary array, one-by-one, and reverse segments). The reverse method was the clear winner, performing the rotation in linear time without taking up extra memory.
* **Complexity (Best):** Time O(n), Space O(1)

### Exercise 6: First Unique Character Finder
We built a hash table (dictionary) to count character frequencies. This let us find the first unique character in linear time instead of getting stuck in slow nested loops.
* **Complexity:** Time O(n), Space O(k)

### Lab 1 Reflection
This lab was a great refresher on core algorithm concepts. We got hands-on experience balancing time complexity against memory usage, especially seeing how hash tables and in-place array tricks significantly speed up our code.

---

## LAB 02: Social Network Algorithms & Data Structures

### Exercise 1: Friend Request Timeline
We built a text parser that scans a message exactly once to count uppercase letters and urgency punctuation. Based on the ratios, it flags the message as "AGGRESSIVE", "URGENT", or "CALM".
* **Complexity:** Time O(N), Space O(1)

### Exercise 2: Mutual Friends Detection Using Sets
We coded our own set operations (Intersection, Difference, Union) to find mutual friends and calculate Jaccard Similarity scores. We also added a feature to recommend 2nd-degree connections.
* **Complexity:** Time O(m + n), Space O(m + n)

### Exercise 3: Friend Recommendation by Common Interests
We calculated Cosine Similarity scores between users based on a shared interest matrix. We then sorted the results to recommend new interests pulled from the top K closest matches.
* **Complexity:** Time O(U * I + U log U), Space O(U + I)

### Exercise 4: Mutual Followers Matrix
We mapped a social network using a 2D boolean Adjacency Matrix. It is incredibly fast for checking specific mutual connections, but the massive grid of "False" values proved it is highly impractical for large user bases.
* **Complexity:** Time O(N^2), Space O(N^2)

### Lab 2 Reflection
We took basic mathematical structures and applied them to real social media features. We learned firsthand how choosing the right data structure (like using Hash Sets over Matrices) makes or breaks a platform as the network scales.

---

## LAB 03: Advanced Data Structures (Linked Lists, Stacks, Queues)

### Exercise 1: Social Media Story Feed
We built a Doubly Linked List to power a bidirectional content feed. It lets us seamlessly swipe forward and backward, tracks view counts, and even reorders the entire feed by popularity using an in-place Bubble Sort.
* **Complexity:** Navigation Time O(1), Sorting Time O(N^2), Space O(1)

### Exercise 2: Activity Feed Processing
We managed notifications and user history using a Queue (FIFO) for incoming alerts and a Stack (LIFO) to track recent user activities. We also added a priority queue feature for urgent alerts.
* **Complexity:** Stack Operations Time O(1), Space O(N)

### Exercise 3: Engagement-Based Priority Queue
We created a custom Priority Queue using a Singly Linked List. Instead of sorting posts by time, it traverses the list upon insertion to rank posts dynamically based on a weighted engagement score (likes, comments, and shares).
* **Complexity:** Insertion Time O(N), Space O(N)

### Lab 3 Reflection
We shifted to node-based structures. We learned how to use Priority Queues to rank a trending feed, Doubly Linked Lists for seamless media swiping, and Stacks/Queues to handle background notifications and undo features.

---

## LAB 04: Recursive Algorithms & Divide and Conquer

### Exercise 1: Recursive Comment Thread Traversal
We built a recursive system to handle deeply nested comment sections. The algorithm navigates tree structures to display threads, count total likes, find the maximum reply depth, search for keywords, and perform cascading deletions to prune entire conversation branches safely.
* **Complexity:** Time O(N) to visit all comments, Space O(D) where D is the maximum reply depth.

### Exercise 2: Content Aggregation with Divide & Conquer
We applied the Divide & Conquer technique to analyze post engagement. By recursively splitting arrays in half, we quickly calculated maximum and average engagement scores, counted posts above specific thresholds, and sorted the feed using a custom Merge Sort. We also built a binary search-style peak hour finder.
* **Complexity:** Merge Sort Time O(N log N), Peak Finder Time O(log N).

### Exercise 3: Converting Recursion to Iteration (Explicit Stacks)
We took our recursive tree algorithms and rewrote them iteratively. By manually using a Stack data structure to flatten comment trees and count nodes, we completely removed the reliance on the system's execution call stack.
* **Complexity:** Time O(N), Space O(D). Memory is stored safely on the heap instead of the fragile call stack.

### Lab 4 Reflection 
This lab showed us both the mathematical beauty and the hidden dangers of recursion. It handles tree structures like nested replies perfectly, but a thread that goes thousands of levels deep will trigger a Stack Overflow and crash the server. Learning to convert recursive logic into iterative stack loops was a game-changer for writing scalable backend code.

---

## LAB 05: Non-Linear Data Structures: Binary and Generalized Trees

### Exercise 1: Binary Tree Metrics & Property Validation
We built a system to manage category hierarchies using Binary Trees. This involved calculating fundamental metrics like tree height, node counts, and leaf counts. We also implemented several validation algorithms to check if a tree is Balanced, Full, Perfect, or Complete. For navigation, we implemented Lowest Common Ancestor (LCA) and path-to-root tracing using parent pointers.
* **Complexity:** Traversal & Metrics Time O(N), Space O(H)

### Exercise 2: Tree Traversals & Content Analytics
We explored different ways to process tree data using In-order, Pre-order, and Post-order traversals. We used Pre-order to serialize hierarchies, In-order to find K-th elements, and Post-order for "bottom-up" analytics like calculating the total post count for a parent category by summing all its children.
* **Complexity:** All Traversals Time O(N), Space O(H)

### Exercise 3: Generalized Trees & Representation Conversion
We moved beyond Binary Trees to Generalized (N-ary) Trees, where a category can have an unlimited number of sub-categories. We implemented the "Left-Child Right-Sibling" representation to convert these N-ary trees into Binary Trees and back again, and calculated advanced metrics like Fan-out and Branching Factor.
* **Complexity:** Tree Conversion Time O(N), Space O(H)

### Lab 5 Reflection & Project Integration
This lab was a major step up because we had to stop thinking linearly. Working with trees showed us how complex hierarchies are handled, but more importantly, all five of these labs have given us the exact architectural foundation we need for our official semester project: **Instagram (Logic replication)**. 

Our core challenge is efficiently processing, storing, and ranking massive multimedia data to ensure low latency and high scalability. Here is how our lab work directly translates to our upcoming system design:
* **Ranking & Recommendations:** We will use Priority Queues alongside Collaborative and Content-based filtering to power our Feed Ranking and Reels Recommendation algorithms.
* **Navigation:** Doubly Linked Lists will allow us to build seamless, instant swiping for Reels and carousel posts.
* **Data Organization:** Generalized Trees will categorize content for the Explore Page, and we will rely on inverted indexing for our Search Algorithm.
* **Real-time Activity:** Stacks and Queues will manage our real-time messaging and notification systems.

We are building the backend with Python, Django, and PostgreSQL, and the frontend with React Native. Armed with these advanced data structures, we believe we are fully ready to tackle the development phase.