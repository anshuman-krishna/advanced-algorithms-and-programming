## Advanced Algorithms and Programming

## Team Members & Contributions
* **YADAV Anshuman Krishna**
  * Lab 1: Exercises 4, 5, 6
  * Lab 2: Exercises 2, 4
  * Lab 3: Exercise 1
* **MAHALINGAM Nithees**
  * Lab 1: Exercises 1, 2, 3
  * Lab 2: Exercise 1
  * Lab 3: Exercise 2
* **SARAVANAN Arun Prasath**
  * Lab 1: Absent
  * Lab 2: Exercise 3
  * Lab 3: Exercise 3

---

# LAB 01: Revision of Algorithms Fundamentals

## Exercise 1: Integer Mirror
We reversed an integer mathematically (`%`, `//`, `*`) without taking the easy route of converting it to a string. 
* **Complexity:** Time O(d) where d is digits, Space O(1)

## Exercise 2: Balanced Symbol Checker
We used a stack to check if brackets in a string are perfectly balanced. We pushed opening brackets onto the stack and popped them when finding a match, returning false if things did not line up.
* **Complexity:** Time O(n), Space O(n)

## Exercise 3: Merge Overlapping Intervals
We sorted intervals by their start times and merged them in a single pass using the `max` function to handle overlapping ends.
* **Complexity:** Time O(n log n), Space O(n)

## Exercise 4: Polynomial Evaluation
We applied Horner's Method to evaluate polynomials iteratively, which drastically cut down on unnecessary mathematical multiplications.
* **Complexity:** Time O(n), Space O(1)

## Exercise 5: Array Rotation Optimization
We tested three rotation methods (temporary array, one-by-one, and reverse segments). The reverse method was the clear winner, performing the rotation in linear time without taking up extra memory.
* **Complexity (Best):** Time O(n), Space O(1)

## Exercise 6: First Unique Character Finder
We built a hash table (dictionary) to count character frequencies. This let us find the first unique character in linear time instead of getting stuck in slow nested loops.
* **Complexity:** Time O(n), Space O(k)

## Lab 1 Reflection
This lab was a great refresher on core algorithm concepts. We got hands-on experience balancing time complexity against memory usage, especially seeing how hash tables and in-place array tricks significantly speed up our code.

---

# LAB 02: Social Network Algorithms & Data Structures

## Exercise 1: Friend Request Timeline
We built a text parser that scans a message exactly once to count uppercase letters and urgency punctuation. Based on the ratios, it flags the message as "AGGRESSIVE", "URGENT", or "CALM".
* **Complexity:** Time O(N), Space O(1)

## Exercise 2: Mutual Friends Detection Using Sets
We coded our own set operations (Intersection, Difference, Union) to find mutual friends and calculate Jaccard Similarity scores. We also added a feature to recommend 2nd-degree connections.
* **Complexity:** Time O(m + n), Space O(m + n)

## Exercise 3: Friend Recommendation by Common Interests
We calculated Cosine Similarity scores between users based on a shared interest matrix. We then sorted the results to recommend new interests pulled from the top K closest matches.
* **Complexity:** Time O(U * I + U log U), Space O(U + I)

## Exercise 4: Mutual Followers Matrix
We mapped a social network using a 2D boolean Adjacency Matrix. It is incredibly fast for checking specific mutual connections, but the massive grid of "False" values proved it is highly impractical for large user bases.
* **Complexity:** Time O(N^2), Space O(N^2)

## Lab 2 Reflection
We took basic mathematical structures and applied them to real social media features. We learned firsthand how choosing the right data structure (like using Hash Sets over Matrices) makes or breaks a platform as the network scales.

---

# LAB 03: Advanced Data Structures (Linked Lists, Stacks, Queues)

## Exercise 1: Social Media Story Feed
We built a Doubly Linked List to power a bidirectional content feed. It lets us seamlessly swipe forward and backward, tracks view counts, and even reorders the entire feed by popularity using an in-place Bubble Sort.
* **Complexity:** Navigation Time O(1), Sorting Time O(N^2), Space O(1)

## Exercise 2: Activity Feed Processing
We managed notifications and user history using a Queue (FIFO) for incoming alerts and a Stack (LIFO) to track recent user activities. We also added a priority queue feature for urgent alerts.
* **Complexity:** Stack Operations Time O(1), Space O(N)

## Exercise 3: Engagement-Based Priority Queue
We created a custom Priority Queue using a Singly Linked List. Instead of sorting posts by time, it traverses the list upon insertion to rank posts dynamically based on a weighted engagement score (likes, comments, and shares).
* **Complexity:** Insertion Time O(N), Space O(N)

## Lab 3 Reflection & Project Integration
We shifted to node-based structures, and these exercises directly inspired our upcoming semester project: a Pinterest-style platform. We plan to use Priority Queues to rank our trending feed, Doubly Linked Lists for seamless media swiping, and Stacks/Queues to handle our background notifications and "undo" features. 

Even if we end up pivoting to a different application idea later, this core architectural foundation will carry over perfectly. We will always need efficient ways to rank content, navigate media, and process events!
---