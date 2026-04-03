## LAB_05 – Non-Linear Data Structures: Binary and Generalized Trees

## Team Members:
- **YADAV Anshuman Krishna** – Exercise 1 & Final Integration
- **MAHALINGAM Nithees** – Exercise 2
- **SARAVANAN Arun Prasath** – Exercise 3

---

## Exercise 1 – Binary Tree Metrics & Property Validation

We built a system to manage category hierarchies using Binary Trees. This involved calculating fundamental metrics like tree height, node counts, and leaf counts. We also implemented several validation algorithms to check if a tree is Balanced, Full, Perfect, or Complete. 

For navigation, we implemented Lowest Common Ancestor (LCA) and path-to-root tracing using parent pointers, allowing us to find the relationship between any two categories in O(N) time.

### Complexity Summary
- Traversal & Metrics: Time O(N), Space O(H)
- Balance Check (Naive): Time O(N²), Space O(H)
- Completeness Check (BFS): Time O(N), Space O(N)

---

## Exercise 2 – Tree Traversals & Content Analytics

We explored different ways to process tree data using In-order, Pre-order, and Post-order traversals. 
- **In-order:** Used to collect category names and find the K-th element.
- **Pre-order:** Used for exporting the tree structure and serializing the hierarchy into a readable string format.
- **Post-order:** Ideal for "bottom-up" analytics, such as calculating the total post count for a parent category by summing all its children, and finding the most popular sub-category.

### Complexity Summary
- All Traversals: Time O(N), Space O(H)
- Serialization: Time O(N), Space O(H)

---

## Exercise 3 – Generalized Trees & Representation Conversion

We moved beyond Binary Trees to Generalized (N-ary) Trees, where a category can have an unlimited number of sub-categories. We implemented the "Left-Child Right-Sibling" representation to convert these N-ary trees into Binary Trees and back again. 

We also defined specific N-ary metrics such as the Fan-out (maximum children of any node) and the Branching Factor (average children across non-leaf nodes) to analyze how "wide" the category structure grows.

### Complexity Summary
- Tree Conversion: Time O(N), Space O(H)
- Metrics (Fan-out/Height): Time O(N), Space O(H)
- Level-order (BFS): Time O(N), Space O(W) where W is max width

---

## Overall Reflection

This lab was a major step up because we had to research a lot about the topics proived to us. Working with trees showed us how complex hierarchies like a social media category system are handled. 

We learned that while recursion makes tree code look very clean, it comes with a hidden cost. For example, our initial balanced check logic was O(N²) because we were recalculating height redundantly. We also saw how converting N-ary trees to Binary representations allows us to apply standard binary algorithms to much more complex, real-world data structures. thanks.