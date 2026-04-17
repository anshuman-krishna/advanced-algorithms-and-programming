# ---------- SIERPINSKI ----------
def sierpinski_count(depth):
    if depth < 0:
        return 0
    return 3 ** depth
def sierpinski_print(depth, indent=0):
    if depth == 0:
        print(" " * indent + "▲")
        return
    sierpinski_print(depth - 1, indent)
    sierpinski_print(depth - 1, indent + 2)
    sierpinski_print(depth - 1, indent + 1)

# ---------- TREE ----------
def draw_tree(depth, indent=0):
    if depth == 0:
        return
    print(" " * indent + "|") 
    draw_tree(depth - 1, indent + 2)
    draw_tree(depth - 1, indent + 2)

# ---------- SPLIT VIEW (QUADTREE STYLE) ----------
def split_view(depth, indent=0):
    if depth == 0:
        print(" " * indent + "[ ]")
        return
    print(" " * indent + "[Split]") 
    split_view(depth - 1, indent + 2)
    split_view(depth - 1, indent + 2)
    split_view(depth - 1, indent + 2)
    split_view(depth - 1, indent + 2)

# ---------- SIMPLE TERRAIN (RECURSIVE HEIGHTS) ----------
def generate_terrain(depth, value=50):
    if depth == 0:
        return [value]
    left = generate_terrain(depth - 1, value - 5)
    right = generate_terrain(depth - 1, value + 5)
 
    return left + [value] + right

# ---------- FRACTAL DIMENSION ----------
def approx_log(x):
    if x <= 0:
        return 0
    return (x - 1) / x
def fractal_dimension(counts, sizes):
    log_counts = []
    log_sizes = []
    for i in range(len(counts)):
        log_counts.append(approx_log(counts[i]))
        log_sizes.append(approx_log(1 / sizes[i])) 
    n = len(log_counts)
    mean_x = sum(log_sizes) / n
    mean_y = sum(log_counts) / n 
    num = 0
    den = 0
    for i in range(n):
        num += (log_sizes[i] - mean_x) * (log_counts[i] - mean_y)
        den += (log_sizes[i] - mean_x) ** 2
    if den == 0:
        return 0  
    return num / den

# ---------- ANOMALY DETECTION ----------
def find_anomalies(data):
    anomalies = []    
    for i in range(1, len(data) - 1):
        if data[i] == data[i-1] == data[i+1]:
            anomalies.append((i, data[i]))    
    return anomalies
print("===== RECURSIVE PATTERN GENERATOR =====")
print("1. Split View")
print("2. Draw Fractal")
print("3. Generate Terrain")
print("4. Measure Dimension")
print("5. Find Anomalies")
choice = int(input("Enter your choice: "))

# ---------- SPLIT VIEW ----------
if choice == 1:
    depth = int(input("Enter depth: "))
    print("\nSplit View:\n")
    split_view(depth)

# ---------- FRACTAL ----------
elif choice == 2:
    print("1. Sierpinski")
    print("2. Tree")
    sub = int(input("Choose fractal: "))   
    depth = int(input("Enter depth: "))    
    if sub == 1:
        sierpinski_print(depth)
        print("Total triangles:", sierpinski_count(depth))
    elif sub == 2:
        draw_tree(depth)

# ---------- TERRAIN ----------
elif choice == 3:
    depth = int(input("Enter terrain depth: "))
    terrain = generate_terrain(depth) 
    print("\nGenerated Terrain:", terrain)

# ---------- DIMENSION ----------
elif choice == 4:
    sizes = [1, 2, 4, 8]
    counts = [10000, 2500, 625, 156]  # square example    
    dim = fractal_dimension(counts, sizes)
    print("\nFractal Dimension:", round(dim, 2))    
    if dim < 1.8 or dim > 2.5:
        print("Warning: Unusual dimension!")

# ---------- ANOMALY ----------
elif choice == 5:
    data = [10, 20, 20, 20, 30, 40, 40, 40, 50]    
    anomalies = find_anomalies(data)    
    print("\nAnomalies found at:")
    for a in anomalies:
        print(a)
else:
    print("Invalid choice")