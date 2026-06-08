def is_valid_invitation(invited, graph):
    n = len(invited)
    for i in range(n):
        u = invited[i]
        for j in range(i + 1, n):
            v = invited[j]
            if v in graph[u]:
                return False
    return True

def find_max_invitations_exact(graph):
    nodes = list(graph.keys())
    best_state = {'size': 0, 'set': []}
    
    def backtrack(index, current_set):
        if index == len(nodes):
            if len(current_set) > best_state['size']:
                best_state['size'] = len(current_set)
                best_state['set'] = list(current_set)
            return
            
        remaining = len(nodes) - index
        if len(current_set) + remaining <= best_state['size']:
            return
            
        candidate = nodes[index]
        can_add = True
        for person in current_set:
            if person in graph[candidate]:
                can_add = False
                break
                
        if can_add:
            current_set.append(candidate)
            backtrack(index + 1, current_set)
            current_set.pop()
            
        backtrack(index + 1, current_set)

    backtrack(0, [])
    return best_state['size'], best_state['set']

def find_max_invitations_greedy(graph):
    invited = []
    available = set(graph.keys())
    
    while available:
        best_node = None
        min_degree = float('inf')
        
        for node in available:
            current_degree = sum(1 for neighbor in graph[node] if neighbor in available)
            if current_degree < min_degree:
                min_degree = current_degree
                best_node = node
                
        invited.append(best_node)
        available.remove(best_node)
        
        for neighbor in list(graph[best_node]):
            if neighbor in available:
                available.remove(neighbor)
                
    return len(invited), invited

# verification
if __name__ == "__main__":
    
    # test case 1: star graph
    star_graph = {
        'Hub': ['A', 'B', 'C', 'D'],
        'A': ['Hub'],
        'B': ['Hub'],
        'C': ['Hub'],
        'D': ['Hub']
    }
    
    # test case 2: full clique
    clique_graph = {
        'P1': ['P2', 'P3', 'P4'],
        'P2': ['P1', 'P3', 'P4'],
        'P3': ['P1', 'P2', 'P4'],
        'P4': ['P1', 'P2', 'P3']
    }

    print("Star Graph Testing:")
    exact_size, exact_set = find_max_invitations_exact(star_graph)
    greedy_size, greedy_set = find_max_invitations_greedy(star_graph)
    print("Exact Max Invitations:", exact_size, "->", exact_set)
    print("Greedy Invitations:", greedy_size, "->", greedy_set)

    print("\nClique Graph Testing:")
    exact_size_c, exact_set_c = find_max_invitations_exact(clique_graph)
    greedy_size_c, greedy_set_c = find_max_invitations_greedy(clique_graph)
    print("Exact Max Invitations:", exact_size_c, "->", exact_set_c)
    print("Greedy Invitations:", greedy_size_c, "->", greedy_set_c)