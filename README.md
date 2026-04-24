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
We implemented two advanced data structures: a Trie for username autocomplete and a Segment Tree for user activity range queries. The Trie enables fast search-as-you-type suggestions, while the Segment Tree efficiently answers range-based analytics such as total posts in the last 7 days or maximum posts in a selected time interval.
* **Complexity:** In the Trie, insertion, search, and prefix lookup run in O(L) where L is the length of the username. Autocomplete runs in O(P + R) where P is prefix length and R is the number of returned suggestions. For the Segment Tree, building runs in O(n), while range sum/min/max queries and updates run in O(log n).
* **Algorithmic Insight:** A Trie is superior to hash maps for prefix matching because it stores shared prefixes compactly and directly supports autocomplete traversal. A Segment Tree is ideal for dynamic analytics because it handles frequent updates efficiently, unlike prefix sum arrays which require O(n) updates.
* **Scalability Reflection:** These structures are highly practical in social media systems. Tries support millions of real-time search queries for usernames, hashtags, or topics, especially when combined with caching and path compression. Segment Trees power dashboards and engagement analytics where user activity changes continuously, making them far more scalable than brute-force range scans.

## Lab 8 Reflection & Project Integration
These three exercises helped me understand how different data structures solve different real-world problems in social media and digital platforms. The Binary Search Tree showed how user profiles can be stored and searched efficiently, while also supporting friend recommendations. The Binary Heap demonstrated how trending posts can be ranked dynamically using fast updates and top-post retrieval. The Trie and Segment Tree showed how autocomplete systems and activity analytics can be handled efficiently.

Overall, I learned that choosing the right data structure is essential for performance and scalability. BSTs are useful for ordered searching, heaps for ranking systems, tries for prefix search, and segment trees for range queries. These exercises showed that modern applications often combine multiple data structures to deliver fast and efficient user experiences.
