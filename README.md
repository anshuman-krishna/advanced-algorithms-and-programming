## LAB 08: More Tree Structures

## Team Members & Contributions
* **YADAV Anshuman Krishna**: Exercise 1
* **MAHALINGAM Nithees**: Exercise 2 & Final Integration
* **SARAVANAN Arun Prasath**: Exercise 3

## Exercise 1: Binary Search Trees – User Search & Friend-of-Friend Suggestions
We implemented a Binary Search Tree (BST) to manage user profiles using user_id as the key, enabling efficient user lookup and friend-of-friend recommendation generation. Each node stores user details such as name and friend connections, making the BST suitable for structured social network data management.
* **Complexity:** Insertion, search, and deletion run in O(log n) on average when the tree is balanced, but degrade to O(n) in the worst case if the BST becomes skewed. Inorder traversal runs in O(n) and returns users sorted by user_id. Friend-of-friend suggestion generation depends on traversing friendship lists, typically O(f^2) where f is the number of friends.
* **Algorithmic Insight:** BSTs are effective when both lookup speed and ordered data retrieval are required. Unlike hash maps, BSTs support sorted traversal naturally, making them useful for ranking users, browsing IDs in order, or performing range-based searches.
* **Scalability Reflection:** For large social networks, an unbalanced BST can reduce performance significantly. Using self-balancing trees such as AVL or Red-Black Trees would maintain O(log n) performance consistently. Combined with graph-based friendship storage, BSTs provide a strong hybrid model for user indexing and recommendation systems.
  
## Exercise 2: Binary Heap – Trending Posts Feed
We implemented a Max-Heap to simulate a real-time trending posts feed where posts are ranked dynamically based on likes. The system supports efficient insertion, updating likes, retrieving the most popular post, and displaying the top K trending posts without sorting the full dataset each time.
* **Complexity:** push(), pop_max(), and update_likes() run in O(log n) due to heap reordering. peek_max() runs in O(1) since the highest-liked post is always at the root. get_top_k(k) runs in O(k log n) by extracting the maximum K times from a temporary heap.
* **Algorithmic Insight:** A Max-Heap is ideal for live ranking systems because it avoids repeated full sorting of posts after every like update. By maintaining only local heap adjustments, it scales efficiently for large social media feeds with continuous engagement updates.
* **Scalability Reflection:** Compared to sorted arrays (O(n) updates), heaps perform significantly better under heavy traffic. This makes them highly suitable for applications such as trending hashtags, video recommendations, breaking news feeds, and gaming leaderboards where rankings change frequently.

## Exercise 3: Prefix and Range Trees – Autocomplete & Activity Range Queries
We applied recursive patterns to procedural generation using the midpoint displacement algorithm. This allowed us to generate randomized terrain data and write a basic artifact detection script to flag harsh, unnatural edges in the data grid.
* **Algorithmic Insight:** The variance of the output is entirely dictated by the mathematical roughness parameter. A value of 0 generates completely flat data, while a high value generates heavily jagged, noisy structures.

## Lab 7 Reflection & Project Integration
This lab pushed us to handle 2D spatial data and exponential recursive algorithms. While the fractal drawing was a great visual exercise for understanding depth limits, the Quadtree logic from Exercise 1 is what directly impacts our backend architecture for our Instagram project. 

If we implement location-based features: such as searching for localized content, finding trending posts in a specific city, or grouping photos on a geographic map-we cannot afford to linearly scan our entire database. We will need to use optimized Quadtree structures to store and retrieve geotagged posts efficiently, ensuring that empty geographic zones are pruned from our search queries to save server memory and keep load times low.
