## LAB 07: Divide & Conquer and Spatial Algorithms

## Team Members & Contributions
* **YADAV Anshuman Krishna**: Exercise 1
* **MAHALINGAM Nithees**: Exercise 2
* **SARAVANAN Arun Prasath**: Exercise 3

## Exercise 1: Spatial Splitting (Quadtrees)
We implemented a recursive algorithm to divide a 2D space into smaller regions to identify dense clusters of data points. This included writing a helper function to count points within specific boundaries and a main function to recursively divide the grid.
* **Complexity:** Time O(N * 4^D) for our naive implementation, Space O(D) where D is the maximum recursion depth.
* **Algorithmic Insight:** We realized that an unoptimized Quadtree wastes massive amounts of processing power by continually splitting empty space. Adding a condition to prune empty branches instantly is critical for real-world performance. We also noted that strict boundary definitions (using `<` instead of `<=`) are required to prevent counting overlapping points twice.

## Exercise 2: Fractal Drawing & Recursive Shapes
We explored recursion through geometric shapes by coding generators for the Sierpinski Triangle and fractal trees. We also wrote an algorithm to calculate the fractal dimension of an image using the box-counting method.
* **Complexity:** O(3^depth) for the Sierpinski Triangle, and O(2^depth) for the fractal tree. Space complexity remains O(depth) for the execution stack.
* **Algorithmic Insight:** Recursion perfectly maps to self-similar structures, but the exponential time complexity means we must strictly limit the maximum depth to prevent the application from freezing.

## Exercise 3: Procedural Generation
We applied recursive patterns to procedural generation using the midpoint displacement algorithm. This allowed us to generate randomized terrain data and write a basic artifact detection script to flag harsh, unnatural edges in the data grid.
* **Algorithmic Insight:** The variance of the output is entirely dictated by the mathematical roughness parameter. A value of 0 generates completely flat data, while a high value generates heavily jagged, noisy structures.

## Lab 7 Reflection & Project Integration
This lab pushed us to handle 2D spatial data and exponential recursive algorithms. While the fractal drawing was a great visual exercise for understanding depth limits, the Quadtree logic from Exercise 1 is what directly impacts our backend architecture for our Instagram project. 

If we implement location-based features—such as searching for localized content, finding trending posts in a specific city, or grouping photos on a geographic map—we cannot afford to linearly scan our entire database. We will need to use optimized Quadtree structures to store and retrieve geotagged posts efficiently, ensuring that empty geographic zones are pruned from our search queries to save server memory and keep load times low.
