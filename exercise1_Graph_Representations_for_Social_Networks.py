class SocialGraph:
    def __init__(self, num_users):
        self.num_users = num_users
        self.num_edges = 0
        self.matrix = [[0 for _ in range(num_users)] for _ in range(num_users)]
        self.adj_list = {i: [] for i in range(num_users)}

    def add_friendship_matrix(self, u, v):
        self.matrix[u][v] = 1
        self.matrix[v][u] = 1
        self.num_edges += 1

    def remove_friendship_matrix(self, u, v):
        self.matrix[u][v] = 0
        self.matrix[v][u] = 0
        self.num_edges -= 1

    def are_friends_matrix(self, u, v):
        if self.matrix[u][v] == 1:
            return True
        return False

    def get_friends_matrix(self, u):
        friends = []
        for i in range(self.num_users):
            if self.matrix[u][i] == 1:
                friends.append(i)
        return friends

    def get_degree_matrix(self, u):
        count = 0
        for i in range(self.num_users):
            if self.matrix[u][i] == 1:
                count += 1
        return count

    def add_friendship_list(self, u, v):
        self.adj_list[u].append(v)
        self.adj_list[v].append(u)
        self.num_edges += 1

    def remove_friendship_list(self, u, v):
        self.adj_list[u].remove(v)
        self.adj_list[v].remove(u)
        self.num_edges -= 1

    def are_friends_list(self, u, v):
        if v in self.adj_list[u]:
            return True
        return False

    def get_friends_list(self, u):
        return self.adj_list[u]

    def get_degree_list(self, u):
        return len(self.adj_list[u])

    def get_num_users(self):
        return self.num_users

    def get_num_edges(self):
        return self.num_edges

    def is_complete_graph(self):
        max_edges = (self.num_users * (self.num_users - 1)) / 2
        if self.num_edges == max_edges:
            return True
        return False

    def graph_density(self):
        if self.num_users <= 1:
            return 0.0
        top = 2 * self.num_edges
        bottom = self.num_users * (self.num_users - 1)
        return top / bottom

    def degree_distribution(self):
        dist = {}
        for user in self.adj_list:
            deg = len(self.adj_list[user])
            if deg in dist:
                dist[deg] += 1
            else:
                dist[deg] = 1
        return dist

    def matrix_to_list(self):
        self.adj_list = {}
        for i in range(self.num_users):
            self.adj_list[i] = []
            for j in range(self.num_users):
                if self.matrix[i][j] == 1:
                    self.adj_list[i].append(j)

    def list_to_matrix(self):
        self.matrix = [[0 for _ in range(self.num_users)] for _ in range(self.num_users)]
        for u in self.adj_list:
            for v in self.adj_list[u]:
                self.matrix[u][v] = 1


# verification
if __name__ == "__main__":
    print("Initializing Social Graph (5 Users):")
    graph = SocialGraph(5)
    
    print("\nTesting Adjacency Matrix:")
    graph.add_friendship_matrix(0, 1)
    graph.add_friendship_matrix(0, 2)
    graph.add_friendship_matrix(1, 3)
    graph.add_friendship_matrix(3, 4)
    
    print(f"Are User 0 and User 1 friends? {graph.are_friends_matrix(0, 1)}")
    print(f"Are User 0 and User 4 friends? {graph.are_friends_matrix(0, 4)}")
    print(f"User 0's friends: {graph.get_friends_matrix(0)}")
    print(f"User 0's degree: {graph.get_degree_matrix(0)}")
    
    print("\nTesting Conversions:")
    print("Converting Matrix to List...")
    graph.matrix_to_list()
    print(f"User 0's friends in Adjacency List: {graph.get_friends_list(0)}")
    
    print("\nTesting Graph Properties:")
    print(f"Total Edges tracked: {graph.get_num_edges()}")
    print(f"Is graph complete? {graph.is_complete_graph()}")
    print(f"Graph Density: {graph.graph_density()}")
    print(f"Degree Distribution: {graph.degree_distribution()}")
    
    print("\nTesting Edge Case (Double Counting):")
    graph.add_friendship_list(0, 1)
    print(f"Added friendship (0,1) again. Total Edges is now: {graph.get_num_edges()}")
    print("Notice how it blindly increments our edge count! A great human error to spot.")