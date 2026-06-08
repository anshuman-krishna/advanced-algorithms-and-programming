import itertools

def is_valid_coverage(selected_users, graph):
    covered = set()
    for user in selected_users:
        covered.add(user)
        for neighbor in graph[user]:
            covered.add(neighbor)
    return len(covered) == len(graph)

def find_minimum_coverage(graph):
    nodes = list(graph.keys())
    n = len(nodes)
    best_size = n + 1
    best_subset = []
    
    for r in range(n + 1):
        for subset in itertools.combinations(nodes, r):
            if is_valid_coverage(subset, graph):
                if len(subset) < best_size:
                    best_size = len(subset)
                    best_subset = list(subset)
                    
    return best_size, best_subset

def find_fast_coverage(graph):
    uncovered = set(graph.keys())
    selected = []
    
    while uncovered:
        best_node = None
        max_covered_count = -1
        
        for node in graph:
            potential_coverage = 0
            if node in uncovered:
                potential_coverage += 1
            for neighbor in graph[node]:
                if neighbor in uncovered:
                    potential_coverage += 1
                    
            if potential_coverage > max_covered_count:
                max_covered_count = potential_coverage
                best_node = node
                
        selected.append(best_node)
        uncovered.discard(best_node)
        for neighbor in graph[best_node]:
            uncovered.discard(neighbor)
            
    return len(selected), selected

# verification

graph_star = {
    'Center': ['L1', 'L2', 'L3', 'L4'],
    'L1': ['Center'],
    'L2': ['Center'],
    'L3': ['Center'],
    'L4': ['Center']
}

graph_line = {
    'A': ['B'],
    'B': ['A', 'C'],
    'C': ['B', 'D'],
    'D': ['C', 'E'],
    'E': ['D', 'F'],
    'F': ['E']
}

print("Testing Star Graph")
print("Validating perfect coverage ['Center']:", is_valid_coverage(['Center'], graph_star))
print("Minimum Coverage (Brute Force):", find_minimum_coverage(graph_star))
print("Fast Coverage (Greedy):", find_fast_coverage(graph_star))

print("\nTesting Line Graph (A-B-C-D-E-F)")
print("Validating perfect coverage ['B', 'E']:", is_valid_coverage(['B', 'E'], graph_line))
print("Minimum Coverage (Brute Force):", find_minimum_coverage(graph_line))
print("Fast Coverage (Greedy):", find_fast_coverage(graph_line))