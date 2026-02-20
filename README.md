# Social Network Algorithms & Data Structures

## Team Members
- **YADAV Anshuman Krishna** – Exercise 2 & 4
- **MAHALINGAM Nithees** – Exercise 1
- **SARAVANAN Arun Prasath** – Exercise 3

---

## Exercise 1 – Friend Request Timeline

A text parsing algorithm used to analyze and classify messages.  
It iterates through the characters exactly once to count uppercase letters, total letters, and specific urgency punctuation marks (`!`, `?`). 

Based on the calculated capitalization ratio and punctuation count, the message is classified as "AGGRESSIVE", "URGENT", or "CALM".

### Complexity Summary
- Time: O(N), where N is the length of the message
- Space: O(1)

---

## Exercise 2 – Mutual Friends Detection Using Sets

Fundamental set operations (Intersection, Difference, Union) are implemented manually to analyze social connections.  
These operations are used to find mutual friends and calculate a Jaccard Similarity score between users.

It also generates second-degree friend recommendations by scanning the friends of a user's direct friends.

### Complexity Summary
- Time: O(m + n) on average for union and similarity comparisons
- Space: O(m + n) to store the resulting sets

---

## Exercise 3 – Friend Recommendation by Common Interests

This algorithm computes similarity scores between a target user and all other users based on an interest matrix.  
It calculates the dot product and vector norms (Cosine Similarity) to find how closely user interests align.

The scores are sorted to find the top K most similar users, which are then used to generate weighted recommendations for new interests.

### Complexity Summary
- Time: O(U × I + U log U), where U is users and I is interests (includes sorting time)
- Space: O(U + I) to store similarity scores and recommendations

---

## Exercise 4 – Mutual Followers Matrix

A social graph is implemented using a 2D boolean array (Adjacency Matrix).  
Rows represent followers and columns represent followees. 

It includes functions to follow/unfollow, retrieve complete follower lists, and calculate an overall influence score. It scans the grid to identify bidirectional (mutual) relationships.

### Complexity Summary
- Time: O(N²) to initialize the matrix and find mutuals across the whole network
- Space: O(N²), which limits its practicality for massive user bases

---

## Overall Reflection

This lab helped us apply fundamental algorithms to real-world social network features. We explored:
- Linear text parsing and classification
- Set operations for relationship mapping
- Adjacency matrices for graph representation
- Similarity scoring (Jaccard and Cosine/Dot Product) for recommendations

by analyzing these different approaches, we gained a practical understanding of how data structure choices (like using a Matrix vs. a Hash Set) directly impact memory limits and processing speed as a network scales.