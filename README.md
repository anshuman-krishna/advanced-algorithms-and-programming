## LAB 07: Divide & Conquer and Spatial Algorithms

## Team Members & Contributions
* **YADAV Anshuman Krishna**: Exercise 1
* **MAHALINGAM Nithees**: Exercise 2 & Final Integration
* **SARAVANAN Arun Prasath**: Exercise 3

## Exercise 1: Spatial Splitting (Quadtrees)
We implemented a recursive algorithm to divide a 2D space into smaller regions to identify dense clusters of data points. This included writing a helper function to count points within specific boundaries and a main function to recursively divide the grid.
* **Complexity:** Time O(N * 4^D) for our naive implementation, Space O(D) where D is the maximum recursion depth.
* **Algorithmic Insight:** We realized that an unoptimized Quadtree wastes massive amounts of processing power by continually splitting empty space. Adding a condition to prune empty branches instantly is critical for real-world performance. We also noted that strict boundary definitions (using `<` instead of `<=`) are required to prevent counting overlapping points twice.

## Exercise 2: Binary Heap – Trending Posts Feed
We implemented a Max-Heap to simulate a real-time trending posts feed where posts are ranked dynamically based on likes. The system supports efficient insertion, updating likes, retrieving the most popular post, and displaying the top K trending posts without sorting the full dataset each time.
* **Complexity:** push(), pop_max(), and update_likes() run in O(log n) due to heap reordering. peek_max() runs in O(1) since the highest-liked post is always at the root. get_top_k(k) runs in O(k log n) by extracting the maximum K times from a temporary heap.
* **Algorithmic Insight:** A Max-Heap is ideal for live ranking systems because it avoids repeated full sorting of posts after every like update. By maintaining only local heap adjustments, it scales efficiently for large social media feeds with continuous engagement updates.
* **Scalability Reflection:** Compared to sorted arrays (O(n) updates), heaps perform significantly better under heavy traffic. This makes them highly suitable for applications such as trending hashtags, video recommendations, breaking news feeds, and gaming leaderboards where rankings change frequently.

## Exercise 3: Procedural Generation
We applied recursive patterns to procedural generation using the midpoint displacement algorithm. This allowed us to generate randomized terrain data and write a basic artifact detection script to flag harsh, unnatural edges in the data grid.
* **Algorithmic Insight:** The variance of the output is entirely dictated by the mathematical roughness parameter. A value of 0 generates completely flat data, while a high value generates heavily jagged, noisy structures.

## Lab 7 Reflection & Project Integration
This lab pushed us to handle 2D spatial data and exponential recursive algorithms. While the fractal drawing was a great visual exercise for understanding depth limits, the Quadtree logic from Exercise 1 is what directly impacts our backend architecture for our Instagram project. 

If we implement location-based features: such as searching for localized content, finding trending posts in a specific city, or grouping photos on a geographic map-we cannot afford to linearly scan our entire database. We will need to use optimized Quadtree structures to store and retrieve geotagged posts efficiently, ensuring that empty geographic zones are pruned from our search queries to save server memory and keep load times low.
