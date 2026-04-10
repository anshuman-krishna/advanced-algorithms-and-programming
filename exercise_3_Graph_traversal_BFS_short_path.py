from collections import deque, defaultdict

class SocialGraph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_user(self, user):
        if user not in self.graph:
            self.graph[user] = []

    def add_friendship(self, user1, user2):
        self.graph[user1].append(user2)
        self.graph[user2].append(user1)

    # Part A - BFS Traversal
    def bfs(self, start_user):
        visited = set([start_user])
        queue = deque([start_user])
        order = []

        while queue:
            user = queue.popleft()
            order.append(user)

            for friend in self.graph[user]:
                if friend not in visited:
                    visited.add(friend)
                    queue.append(friend)

        return order

    # Part B - BFS with Distances
    def bfs_with_distances(self, start_user):
        visited = set([start_user])
        queue = deque([start_user])
        distance = {start_user: 0}

        while queue:
            user = queue.popleft()

            for friend in self.graph[user]:
                if friend not in visited:
                    visited.add(friend)
                    queue.append(friend)
                    distance[friend] = distance[user] + 1

        return distance

    # Part C - Shortest Path
    def shortest_path(self, start_user, target_user):
        visited = set([start_user])
        queue = deque([start_user])
        parent = {start_user: None}

        while queue:
            user = queue.popleft()

            if user == target_user:
                break

            for friend in self.graph[user]:
                if friend not in visited:
                    visited.add(friend)
                    queue.append(friend)
                    parent[friend] = user

        if target_user not in parent:
            return []

        path = []
        current = target_user

        while current is not None:
            path.append(current)
            current = parent[current]

        return path[::-1]

    # Part D - Degrees of Separation
    def degrees_of_separation(self, start_user, target_user):
        distances = self.bfs_with_distances(start_user)
        return distances.get(target_user, -1)

    # Part E - Users Within K Hops
    def friends_within_k_hops(self, start_user, k):
        distances = self.bfs_with_distances(start_user)
        return {user for user, d in distances.items() if d <= k}

    # Average Degrees
    def compute_average_degrees_of_separation(self):
        total = 0
        count = 0

        for user in self.graph:
            distances = self.bfs_with_distances(user)
            for d in distances.values():
                total += d
                count += 1

        return total / count if count else 0

    # Distance Distribution
    def get_distance_distribution(self, start_user):
        distances = self.bfs_with_distances(start_user)
        distribution = {}

        for d in distances.values():
            distribution[d] = distribution.get(d, 0) + 1

        return distribution

    # Friend Recommendation
    def recommend_friends(self, start_user, max_recommendations=5):
        distances = self.bfs_with_distances(start_user)
        suggestions = [user for user, d in distances.items() if d == 2]
        return suggestions[:max_recommendations]