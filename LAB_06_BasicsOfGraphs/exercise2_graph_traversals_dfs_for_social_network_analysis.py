class GraphDFS:
    def __init__(self, graph):
        self.graph = graph
    def dfs_iterative(self, start):
        visited = set()
        stack = [start]
        result = []
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                result.append(node)
                stack.extend(reversed(self.graph.get(node, [])))
        return result
    def find_connected_components(self):
        visited = set()
        components = []
        for node in self.graph:
            if node not in visited:
                stack = [node]
                component = []
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr)
                        component.append(curr)
                        stack.extend(self.graph.get(curr, []))
                components.append(component)
        return components
    def is_connected(self):
        if not self.graph:
            return True
        start = next(iter(self.graph))
        return len(self.dfs_iterative(start)) == len(self.graph)
    def has_path(self, start, target):
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node not in visited:
                visited.add(node)
                stack.extend(self.graph.get(node, []))
        return False
    def find_path(self, start, target):
        visited = set()
        parent = {}
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                if node == target:
                    break
                for neighbor in self.graph.get(node, []):
                    if neighbor not in visited:
                        parent[neighbor] = node
                        stack.append(neighbor)

        if target not in visited:
            return []
        path = []
        curr = target
        while curr != start:
            path.append(curr)
            curr = parent[curr]
        path.append(start)
        return path[::-1]
    def get_component_sizes(self):
        return [len(c) for c in self.find_connected_components()]
    def find_largest_component(self):
        return max(self.find_connected_components(), key=len)
    def find_isolated_users(self):
        return [node for node in self.graph if len(self.graph[node]) == 0]

n = int(input("Enter number of users (nodes): "))
graph = {}
print("Enter neighbors (space-separated) for each user:")
for i in range(1, n + 1):
    neighbors = list(map(int, input(f"User {i}: ").split()))
    graph[i] = neighbors
g = GraphDFS(graph)
start = int(input("Enter start node: "))
target = int(input("Enter target node: "))

print("\nDFS Traversal:", g.dfs_iterative(start))
print("Connected Components:", g.find_connected_components())
print("Is Connected:", g.is_connected())
print("Has Path:", g.has_path(start, target))
print("Path:", g.find_path(start, target))
print("Component Sizes:", g.get_component_sizes())
print("Largest Component:", g.find_largest_component())
print("Isolated Users:", g.find_isolated_users())