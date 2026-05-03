## Advanced Algorithms and Programming

## Team Members & Contributions

**YADAV Anshuman Krishna**
* Lab 1: Exercises 4, 5, 6
* Lab 2: Exercises 2, 4
* Lab 3: Exercise 1
* Lab 4: Exercise 1
* Lab 5: Exercise 1 & Final Integration
* Lab 6: Exercise 1 & Final Integration
* Lab 7: Exercise 1
* Lab 8: Exercise 1

**MAHALINGAM Nithees**
* Lab 1: Exercises 1, 2, 3
* Lab 2: Exercise 1
* Lab 3: Exercise 2
* Lab 4: Exercise 2
* Lab 5: Exercise 2
* Lab 6: Exercise 2 & Final Integration
* Lab 7: Exercise 2 & Final Integration
* Lab 8: Exercise 2 & Final Integration

**SARAVANAN Arun Prasath**
* Lab 1: Absent
* Lab 2: Exercise 3
* Lab 3: Exercise 3
* Lab 4: Exercise 3
* Lab 5: Exercise 3
* Lab 6: Exercise 3
* Lab 7: Exercise 3
* Lab 8: Exercise 3

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
This lab showed us both the mathematical beauty and the hidden dangers of recursion. It handles tree structures like nested replies perfectly, but a thread that goes thousands of levels deep will trigger a Stack Overflow and crash the server. Learning to convert recursive logic into iterative stack loops was a game changer for writing scalable backend code.

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

### Lab 5 Reflection
Working with trees showed us how complex hierarchies are handled. We learned that while recursion makes tree code look very clean, it comes with a hidden cost (like redundant height recalculations if we aren't careful). Converting N-ary trees to Binary representations allowed us to apply standard algorithms to much more complex, real-world data structures.

---

## LAB 06: Basics of Graph Structures

### Exercise 1: Graph Representations for Social Networks
We built the foundation of our social network using both Adjacency Matrices and Adjacency Lists. We implemented core operations like adding friendships, checking connections, calculating network density, and converting between the two formats.
* **Complexity:** Time O(1) for Matrix lookups but O(V) for List lookups.

### Exercise 2: DFS Traversals for Social Network Analysis
We explored Depth-First Search (DFS) to map out user communities. We built both recursive and iterative versions to find connected components, check overall graph connectivity, and trace paths between specific users.
* **Complexity:** Time O(V + E), Space O(V) for the visited sets and stack.

### Exercise 3: BFS Traversals for Shortest Path Analysis
We implemented Breadth-First Search (BFS) to handle distance based features. This allowed us to calculate degrees of separation, find the absolute shortest path between two users, and build a basic friend recommendation engine by looking at second degree connections.
* **Complexity:** Time O(V + E), Space O(V) for the queue.

### Lab 6 & Final Project Integration (Instagram)
All of these labs have given us the exact architectural foundation we need for our official semester project: **Instagram**.

Our core challenge is efficiently processing, storing, and ranking massive amounts of data to ensure low latency and high scalability. Here is how our lab work translates to our upcoming system design:
* **The Follow Graph:** Lab 6 proved that an Adjacency Matrix for a billion users would require an Exabyte of RAM. We will strictly use Adjacency Lists to map our follower relationships.
* **Ranking & Recommendations:** We will use Priority Queues alongside Breadth-First Search (BFS) to power our Feed Ranking and "Suggested Friends" algorithms.
* **Navigation:** Doubly Linked Lists will allow us to build seamless, instant swiping for Reels and carousel posts.
* **Data Organization:** Generalized Trees will categorize content for the Explore Page, and iterative DFS will map out isolated user communities.
* **Real-time Activity:** Stacks and Queues will manage our direct messaging and real time notification systems.

We are building the backend with Python, Django, and PostgreSQL, and the frontend with React Native. Suited with these advanced data structures, we are quite ready to transition into the development phase.

---

## LAB 07: Divide & Conquer and Spatial Algorithms

### Exercise 1: Spatial Splitting (Quadtrees)
We implemented a recursive algorithm to divide a 2D space into smaller regions to identify dense clusters of data points. This included writing a helper function to count points within specific boundaries and a main function to recursively divide the grid.
* **Complexity:** Time O(N * 4^D) for our naive implementation, Space O(D) where D is the maximum recursion depth.
* **Algorithmic Insight:** We realized that an unoptimized Quadtree wastes massive amounts of processing power by continually splitting empty space. Adding a condition to prune empty branches instantly is critical for real-world performance. We also noted that strict boundary definitions (using `<` instead of `<=`) are required to prevent counting overlapping points twice.

### Exercise 2: Fractal Drawing & Recursive Shapes
We explored recursion through geometric shapes by coding generators for the Sierpinski Triangle and fractal trees. We also wrote an algorithm to calculate the fractal dimension of an image using the box-counting method.
* **Complexity:** O(3^depth) for the Sierpinski Triangle, and O(2^depth) for the fractal tree. Space complexity remains O(depth) for the execution stack.
* **Algorithmic Insight:** Recursion perfectly maps to self-similar structures, but the exponential time complexity means we must strictly limit the maximum depth to prevent the application from freezing.

### Exercise 3: Procedural Generation
We applied recursive patterns to procedural generation using the midpoint displacement algorithm. This allowed us to generate randomized terrain data and write a basic artifact detection script to flag harsh, unnatural edges in the data grid.
* **Algorithmic Insight:** The variance of the output is entirely dictated by the mathematical roughness parameter. A value of 0 generates completely flat data, while a high value generates heavily jagged, noisy structures.

### Lab 7 Reflection & Project Integration
This lab pushed us to handle 2D spatial data and exponential recursive algorithms. While the fractal drawing was a great visual exercise for understanding depth limits, the Quadtree logic from Exercise 1 is what directly impacts our backend architecture for our Instagram project. 

If we implement location-based features, such as searching for localized content, finding trending posts in a specific city, or grouping photos on a geographic map, we cannot afford to linearly scan our entire database. We will need to use optimized Quadtree structures to store and retrieve geotagged posts efficiently, ensuring that empty geographic zones are pruned from our search queries to save server memory and keep load times low.

---

## LAB 08: More Tree Structures

### Exercise 1: Binary Search Trees: User Search & Friend-of-Friend Suggestions
We implemented a Binary Search Tree (BST) to manage user profiles using user_id as the key, enabling efficient user lookup and friend-of-friend recommendation generation. Each node stores user details such as name and friend connections, making the BST suitable for structured social network data management.
* **Complexity:** Insertion, search, and deletion run in O(log n) on average when the tree is balanced, but degrade to O(n) in the worst case if the BST becomes skewed. Inorder traversal runs in O(n) and returns users sorted by user_id. Friend-of-friend suggestion generation depends on traversing friendship lists, typically O(f^2) where f is the number of friends.
* **Algorithmic Insight:** BSTs are effective when both lookup speed and ordered data retrieval are required. Unlike hash maps, BSTs support sorted traversal naturally, making them useful for ranking users, browsing IDs in order, or performing range-based searches.
* **Scalability Reflection:** For large social networks, an unbalanced BST can reduce performance significantly. Using self-balancing trees such as AVL or Red-Black Trees would maintain O(log n) performance consistently. Combined with graph-based friendship storage, BSTs provide a strong hybrid model for user indexing and recommendation systems.
  
### Exercise 2: Binary Heap: Trending Posts Feed
We implemented a Max-Heap to simulate a real-time trending posts feed where posts are ranked dynamically based on likes. The system supports efficient insertion, updating likes, retrieving the most popular post, and displaying the top K trending posts without sorting the full dataset each time.
* **Complexity:** push(), pop_max(), and update_likes() run in O(log n) due to heap reordering. peek_max() runs in O(1) since the highest-liked post is always at the root. get_top_k(k) runs in O(k log n) by extracting the maximum K times from a temporary heap.
* **Algorithmic Insight:** A Max-Heap is ideal for live ranking systems because it avoids repeated full sorting of posts after every like update. By maintaining only local heap adjustments, it scales efficiently for large social media feeds with continuous engagement updates.
* **Scalability Reflection:** Compared to sorted arrays (O(n) updates), heaps perform significantly better under heavy traffic. This makes them highly suitable for applications such as trending hashtags, video recommendations, breaking news feeds, and gaming leaderboards where rankings change frequently.

### Exercise 3: Prefix and Range Trees: Autocomplete & Activity Range Queries
We implemented two advanced data structures: a Trie for username autocomplete and a Segment Tree for user activity range queries. The Trie enables fast search-as-you-type suggestions, while the Segment Tree efficiently answers range-based analytics such as total posts in the last 7 days or maximum posts in a selected time interval.
* **Complexity:** In the Trie, insertion, search, and prefix lookup run in O(L) where L is the length of the username. Autocomplete runs in O(P + R) where P is prefix length and R is the number of returned suggestions. For the Segment Tree, building runs in O(n), while range sum/min/max queries and updates run in O(log n).
* **Algorithmic Insight:** A Trie is superior to hash maps for prefix matching because it stores shared prefixes compactly and directly supports autocomplete traversal. A Segment Tree is ideal for dynamic analytics because it handles frequent updates efficiently, unlike prefix sum arrays which require O(n) updates.
* **Scalability Reflection:** These structures are highly practical in social media systems. Tries support millions of real-time search queries for usernames, hashtags, or topics, especially when combined with caching and path compression. Segment Trees power dashboards and engagement analytics where user activity changes continuously, making them far more scalable than brute-force range scans.

### Lab 8 Reflection & Project Integration
These three exercises helped our team understand how different data structures solve different real-world problems in social media and digital platforms. The Binary Search Tree showed how user profiles can be stored and searched efficiently, while also supporting friend recommendations. The Binary Heap demonstrated how trending posts can be ranked dynamically using fast updates and top-post retrieval. The Trie and Segment Tree showed how autocomplete systems and activity analytics can be handled efficiently.

Overall, we learned that choosing the right data structure is essential for performance and scalability. BSTs are useful for ordered searching, heaps for ranking systems, tries for prefix search, and segment trees for range queries. These exercises showed us that modern applications often combine multiple data structures to deliver fast and efficient user experiences.
