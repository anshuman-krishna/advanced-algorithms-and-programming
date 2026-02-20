class FollowerMatrix:
    def __init__(self, n):
        self.size = n
        self.matrix = [[False for _ in range(n)] for _ in range(n)]

    def follow(self, follower, followee):
        self.matrix[follower][followee] = True

    def unfollow(self, follower, followee):
        self.matrix[follower][followee] = False

    def is_following(self, follower, followee):
        return self.matrix[follower][followee]

    def get_followers(self, user):
        followers_list = []
        for i in range(self.size):
            if self.matrix[i][user] == True:
                followers_list.append(i)
        return followers_list

    def get_following(self, user):
        following_list = []
        for i in range(self.size):
            if self.matrix[user][i] == True:
                following_list.append(i)
        return following_list

    def find_mutual_follows(self):
        mutuals = []
        for i in range(self.size):
            for j in range(self.size):
                is_following = self.matrix[i][j]
                is_followed_back = self.matrix[j][i]
                
                if i != j and is_following and is_followed_back:
                    mutuals.append((i, j))
        return mutuals

    def calculate_influence(self, user):
        followers = len(self.get_followers(user))
        following = len(self.get_following(user))
        total_score = followers + following
        return total_score / self.size
    
# initialize
graph = FollowerMatrix(3)

# 1. normal case
graph.follow(0, 1)
graph.follow(1, 0)
graph.follow(1, 2)

print(f"Followers of User 2 (index 1): {graph.get_followers(1)}")
print(f"User 2 follows: {graph.get_following(1)}")

print(f"Mutual Follows: {graph.find_mutual_follows()}") 

print(f"Influence of User 2: {graph.calculate_influence(1)}") 

# 2. edge case, self-following
graph.follow(2, 2)
print(f"Mutuals ignores self: {graph.find_mutual_follows()}")

# 3. edge case: unfollowing
graph.unfollow(1, 0)
print(f"Mutuals after unfollow: {graph.find_mutual_follows()}")