# ---------- SIERPINSKI ----------
def sierpinski_count(depth):
    if depth < 0:
        return 0
    return 3 ** depth
def sierpinski_print(depth, indent=0):
    if depth == 0:
        print(" " * indent + "🔺")
        return   
    sierpinski_print(depth - 1, indent)
    sierpinski_print(depth - 1, indent + 2)
    sierpinski_print(depth - 1, indent + 1)

# ---------- FRACTAL TREE ----------
def draw_tree(depth, indent=0):
    if depth == 0:
        return   
    print(" " * indent + "|")  
    draw_tree(depth - 1, indent + 2)
    draw_tree(depth - 1, indent + 2)
def approx_log(x):
    if x <= 0:
        return 0
    return (x - 1) / x   # simple approximation
# ---------- FRACTAL DIMENSION ----------
def fractal_dimension(counts, sizes):
    log_counts = []
    log_sizes = [] 
    for i in range(len(counts)):
        log_counts.append(approx_log(counts[i]))
        log_sizes.append(approx_log(1 / sizes[i]))  
    n = len(log_counts)  
    mean_x = sum(log_sizes) / n
    mean_y = sum(log_counts) / n 
    numerator = 0
    denominator = 0 
    for i in range(n):
        numerator += (log_sizes[i] - mean_x) * (log_counts[i] - mean_y)
        denominator += (log_sizes[i] - mean_x) ** 2
    if denominator == 0:
        return 0 
    return numerator / denominator
print("===== FRACTAL PROGRAM =====")
print("1. Sierpinski Triangle")
print("2. Fractal Tree")
print("3. Fractal Dimension")

choice = int(input("Enter your choice: "))

# ---------- SIERPINSKI ----------
if choice == 1:
    depth = int(input("Enter depth: "))
    print("\nSierpinski Structure:\n")
    sierpinski_print(depth)
    print("\nTotal triangles:", sierpinski_count(depth))

# ---------- TREE ----------
elif choice == 2:
    depth = int(input("Enter depth: "))
    print("\nFractal Tree:\n")
    draw_tree(depth)

# ---------- FRACTAL DIMENSION ----------
elif choice == 3:
    print("\nChoose shape:")
    print("1. Line")
    print("2. Square")
    shape = int(input("Enter choice: "))
    sizes = [1, 2, 4, 8]
    if shape == 1:
        counts = [100, 50, 25, 12]   # linear scaling
    elif shape == 2:
        counts = [10000, 2500, 625, 156]  # square scaling
    else:
        print("Invalid choice")
        counts = []
    if counts:
        dim = fractal_dimension(counts, sizes)
        print("\nApprox Fractal Dimension:", round(dim, 2))
else:
    print("Invalid main choice")
