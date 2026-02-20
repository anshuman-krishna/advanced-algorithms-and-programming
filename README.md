# Advanced Algorithms and Programming

## Team Members & Contributions
* **YADAV Anshuman Krishna**
  * Lab 1: Exercises 4, 5, 6
  * Lab 2: Exercises 2, 4
* **MAHALINGAM Nithees**
  * Lab 1: Exercises 1, 2, 3
  * Lab 2: Exercise 1
* **SARAVANAN Arun Prasath**
  * Lab 1: Absent
  * Lab 2: Exercise 3

---

# LAB 01: Revision of Algorithms Fundamentals

## Exercise 1: Integer Mirror
The integer is reversed using only mathematical operations (`%`, `//`, `*`).  
Each digit is extracted using modulo and added to the reversed number after shifting the previous result.
No string conversion is used.

### Complexity Summary
* Time: O(d), where d is the number of digits  
* Space: O(1)

## Exercise 2: Balanced Symbol Checker
A stack-based approach is used to verify whether the brackets are balanced.
Opening brackets are pushed into a list (used as a stack).  
When a closing bracket is found, the top element is checked using a dictionary that stores matching pairs.
If any mismatch or early closing bracket is found, the function returns `False`.  
At the end, the string is balanced only if the stack is empty.

### Complexity Summary
* Time: O(n), where n is the length of the string  
* Space: O(n) in the worst case (all opening brackets)

## Exercise 3: Merge Overlapping Intervals
The intervals are first sorted based on their starting values.  
Then the list is scanned and overlapping intervals are merged by comparing the current interval with the next one.
If they overlap, the end value is updated using `max`.  
Otherwise, the interval is added to the result list.

### Complexity Summary
* Time: O(n log n) due to sorting  
* Space: O(n)

## Exercise 4: Polynomial Evaluation (Horner's Method)
The polynomial is evaluated using Horner's Method.  
Instead of computing powers separately, the result is built iteratively from the highest degree coefficient to the lowest.
This significantly reduces unnecessary multiplications.

### Complexity Summary
* Time: O(n)  
* Space: O(1)

## Exercise 5: Array Rotation Optimization
Three approaches were implemented:
1. Temporary array method  
2. Rotate one-by-one method  
3. Reverse segments method  

The temporary array method is simple but uses extra memory.  
The one-by-one method is straightforward but inefficient when k is large.  
The reverse method performs the rotation in linear time with constant extra space.

### Complexity Summary
* Temporary array: Time O(n), Space O(n)  
* One-by-one: Time O(nk), Space O(1)  
* Reverse method: Time O(n), Space O(1)

## Exercise 6: First Unique Character Finder
A dictionary (hash table) is used to count character frequencies.  
The string is scanned to find the first character with frequency equal to one.
This avoids nested loops and ensures linear time performance.

### Complexity Summary
* Time: O(n)  
* Space: O(k) where k is the alphabet size (O(1) if fixed)

## Lab 1 Reflection
This lab helped us revise fundamental algorithm concepts such as mathematical digit manipulation, stack usage for pattern matching, sorting and interval merging, in-place array operations, and efficient use of hash tables. Different approaches were compared to better understand trade-offs between time complexity and memory usage.

---

# LAB 02: Social Network Algorithms & Data Structures

## Exercise 1: Friend Request Timeline
A text parsing algorithm used to analyze and classify messages.  
It iterates through the characters exactly once to count uppercase letters, total letters, and specific urgency punctuation marks (`!`, `?`). 
Based on the calculated capitalization ratio and punctuation count, the message is classified as "AGGRESSIVE", "URGENT", or "CALM".

### Complexity Summary
* Time: O(N), where N is the length of the message
* Space: O(1)

## Exercise 2: Mutual Friends Detection Using Sets
Fundamental set operations (Intersection, Difference, Union) are implemented manually to analyze social connections.  
These operations are used to find mutual friends and calculate a Jaccard Similarity score between users.
It also generates second-degree friend recommendations by scanning the friends of a user's direct friends.

### Complexity Summary
* Time: O(m + n) on average for union and similarity comparisons
* Space: O(m + n) to store the resulting sets

## Exercise 3: Friend Recommendation by Common Interests
This algorithm computes similarity scores between a target user and all other users based on an interest matrix.  
It calculates the dot product and vector norms (Cosine Similarity) to find how closely user interests align.
The scores are sorted to find the top K most similar users, which are then used to generate weighted recommendations for new interests.

### Complexity Summary
* Time: O(U * I + U log U), where U is users and I is interests (includes sorting time)
* Space: O(U + I) to store similarity scores and recommendations

## Exercise 4: Mutual Followers Matrix
A social graph is implemented using a 2D boolean array (Adjacency Matrix).  
Rows represent followers and columns represent followees. 
It includes functions to follow/unfollow, retrieve complete follower lists, and calculate an overall influence score. It scans the grid to identify bidirectional (mutual) relationships.

### Complexity Summary
* Time: O(N^2) to initialize the matrix and find mutuals across the whole network
* Space: O(N^2), which limits its practicality for massive user bases

## Lab 2 Reflection
This lab helped us apply fundamental algorithms to real-world social network features. We explored linear text parsing and classification, set operations for relationship mapping, adjacency matrices for graph representation, and similarity scoring (Jaccard and Cosine/Dot Product) for recommendations. By analyzing these different approaches, we gained a practical understanding of how data structure choices (like using a Matrix vs. a Hash Set) directly impact memory limits and processing speed as a network scales.