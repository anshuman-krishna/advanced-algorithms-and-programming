## LAB_04 - Recursive Algorithms & Divide and Conquer

## Team Members:
* **YADAV Anshuman Krishna** - Exercise 1
* **MAHALINGAM Nithees** - Exercise 2
* **SARAVANAN Arun Prasath** - Exercise 3

---

## Exercise 1 - Recursive Comment Thread Traversal

We built a recursive system to handle deeply nested social media comment sections. 
The algorithm navigates tree structures to display threads, count total likes, find the maximum reply depth, search for keywords, and perform cascading deletions to safely prune entire conversation branches.

### Complexity Summary
* Time: O(N) to visit all comments in a thread
* Space: O(D), where D is the maximum reply depth (stored on the system call stack)

---

## Exercise 2 - Content Aggregation with Divide and Conquer

We applied the Divide and Conquer technique to analyze post engagement data efficiently. 
By recursively splitting arrays in half, we calculated maximum and average engagement scores, counted posts above specific thresholds, and sorted the feed using a custom Merge Sort. We also implemented a binary search style algorithm to efficiently find peak traffic hours.

### Complexity Summary
* Time: O(N log N) for the Merge Sort, and O(log N) for the peak hour search
* Space: O(N) for the temporary arrays used during the merging process

---

## Exercise 3 - Converting Recursion to Iteration (Explicit Stacks)

We took our recursive tree algorithms and rewrote them iteratively to make them production-safe. 
By manually using a Stack data structure to flatten comment trees and count nodes, we completely removed our reliance on the system's fragile execution call stack.

### Complexity Summary
* Time: O(N) to traverse the comments
* Space: O(D) for the manual stack, but stored safely on the massive heap memory instead of the limited call stack

---

## Overall Reflection

This lab showed us both the mathematical beauty and the hidden dangers of recursion. It handles tree structures like nested replies perfectly, but a thread that goes thousands of levels deep will quickly trigger a Stack Overflow and crash the server. 

Learning to convert recursive logic into iterative stack loops was a game changer for writing scalable backend code. All of these exercises have given us the exact architectural foundation we need to safely manage infinitely nested data for our upcoming semester project.