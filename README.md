## LAB 06: Basics of Graph Structures

## Team Members & Contributions

- **YADAV Anshuman Krishna**: Exercise 1
- **MAHALINGAM Nithees**: Exercise 2 & Final Integration
- **SARAVANAN Arun Prasath**: Exercise 3

### Exercise 1: Graph Representations for Social Networks

We built the foundation of our social network using both Adjacency Matrices and Adjacency Lists. We implemented core operations like adding friendships, checking connections, calculating network density, and converting between the two formats.

- **Complexity:** Time O(1) for Matrix lookups but O(V) for List lookups.
- **Memory Insight:** We calculated that an Adjacency Matrix for a billion users would require an Exabyte of RAM. This shows that Adjacency Lists are the more practical option for scaling our backend.

### Exercise 2: DFS Traversals for Social Network Analysis

We explored Depth-First Search (DFS) to map out user communities. We built both recursive and iterative versions to find connected components, check overall graph connectivity, and trace paths between specific users.

- **Complexity:** Time O(V + E), Space O(V) for the visited sets and stack.
- **Scale Insight:** We noted that recursive DFS can crash the server with a Stack Overflow on deep networks, meaning an iterative stack approach is much safer for production.

### Exercise 3: BFS Traversals for Shortest Path Analysis

We implemented Breadth-First Search (BFS) to handle distance based features. This allowed us to calculate degrees of separation, find the absolute shortest path between two users, and build a basic friend recommendation engine by looking at second degree connections.

- **Complexity:** Time O(V + E), Space O(V) for the queue.
- **Algorithmic Insight:** BFS naturally explores level by level, making it mathematically reliable to find the shortest friendship chain in an unweighted graph.

### Lab 6 Reflection & Project Integration

This lab provided a realistic look at how we need to structure user relationships for our Instagram project. Running the memory calculations made it clear that Adjacency Lists are the only viable option for our database.

As we move into building the actual application, we plan to use BFS to power our recommendation algorithms and track degrees of separation. For mapping larger user communities, we will stick to iterative DFS to keep our backend stable and avoid recursion crashes as our network grows.
