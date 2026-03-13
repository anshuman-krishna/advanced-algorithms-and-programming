## LAB_01 – Revision of Algorithms’ Fundamentals

## Team Members
- **YADAV Anshuman Krishna** – Exercise 4, 5 & 6  
- **MAHALINGAM Nithees** – Exercise 1, 2 & 3  
- **SARAVANAN Arun Prasath** – Absent  

---

## Exercise 1 – Integer Mirror

The integer is reversed using only mathematical operations (`%`, `//`, `*`).  
Each digit is extracted using modulo and added to the reversed number after shifting the previous result.

No string conversion is used.

### Complexity Summary
- Time: O(d), where d is the number of digits  
- Space: O(1)

---

## Exercise 2 – Balanced Symbol Checker

A stack-based approach is used to verify whether the brackets are balanced.

Opening brackets are pushed into a list (used as a stack).  
When a closing bracket is found, the top element is checked using a dictionary that stores matching pairs.

If any mismatch or early closing bracket is found, the function returns `False`.  
At the end, the string is balanced only if the stack is empty.

### Complexity Summary
- Time: O(n), where n is the length of the string  
- Space: O(n) in the worst case (all opening brackets)

---

## Exercise 3 – Merge Overlapping Intervals

The intervals are first sorted based on their starting values.  
Then the list is scanned and overlapping intervals are merged by comparing the current interval with the next one.

If they overlap, the end value is updated using `max`.  
Otherwise, the interval is added to the result list.

### Complexity Summary
- Time: O(n log n) due to sorting  
- Space: O(n)

---

## Exercise 4 – Polynomial Evaluation (Horner’s Method)

The polynomial is evaluated using Horner’s Method.  
Instead of computing powers separately, the result is built iteratively from the highest degree coefficient to the lowest.

This significantly reduces unnecessary multiplications.

### Complexity Summary
- Time: O(n)  
- Space: O(1)

---

## Exercise 5 – Array Rotation Optimization

Three approaches were implemented:

1. Temporary array method  
2. Rotate one-by-one method  
3. Reverse segments method  

The temporary array method is simple but uses extra memory.  
The one-by-one method is straightforward but inefficient when k is large.  
The reverse method performs the rotation in linear time with constant extra space.

### Complexity Summary
- Temporary array: Time O(n), Space O(n)  
- One-by-one: Time O(nk), Space O(1)  
- Reverse method: Time O(n), Space O(1)

---

## Exercise 6 – First Unique Character Finder

A dictionary (hash table) is used to count character frequencies.  
The string is scanned to find the first character with frequency equal to one.

This avoids nested loops and ensures linear time performance.

### Complexity Summary
- Time: O(n)  
- Space: O(σ)  
  - Worst case: O(n)  
  - If alphabet size is fixed: O(1)

---

## Overall Reflection

This lab helped us revise fundamental algorithm concepts such as:
- Mathematical digit manipulation  
- Stack usage for pattern matching  
- Sorting and interval merging  
- In-place array operations  
- Efficient use of hash tables  

different approaches were compared to better understand trade-offs between time complexity and memory usage.
