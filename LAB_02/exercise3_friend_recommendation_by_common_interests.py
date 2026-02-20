def cosine_similarity(user_a, user_b):
    dot = 0
    norm_a = 0
    norm_b = 0
    for i in range(len(user_a)):
        dot += user_a[i] * user_b[i]
        norm_a += user_a[i] * user_a[i]
        norm_b += user_b[i] * user_b[i]
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / ((norm_a ** 0.5) * (norm_b ** 0.5))

def recommend_friends(Users, FriendList, userID, K):
    U = len(Users)
    I = len(Users[0])
    scores = []
    for u in range(U):
        if u != userID and u not in FriendList[userID]:
            sim = cosine_similarity(Users[userID], Users[u])
            scores.append((u, sim))
    scores.sort(key=lambda x: x[1], reverse=True)
    TopK = scores[:K]
    rec = [0] * I
    for pair in TopK:
        u = pair[0]
        sim = pair[1]
        for i in range(I):
            if Users[userID][i] == 0:
                rec[i] += Users[u][i] * sim
    return TopK, rec

U = int(input("Enter number of users: "))
I = int(input("Enter number of interests: "))
Users = []
print("Enter user-interest matrix (space separated values for each user):")
for u in range(U):
    row = list(map(int, input(f"User {u}: ").split()))
    Users.append(row)
FriendList = {}
print("Enter friend list for each user (space separated user IDs, or press Enter for none):")
for u in range(U):
    friends_input = input(f"Friends of user {u}: ").strip()
    if friends_input == "":
        FriendList[u] = []
    else:
        FriendList[u] = list(map(int, friends_input.split()))
userID = int(input("Enter target user ID: "))
K = int(input("Enter value of K: "))
TopK, recommendations = recommend_friends(Users, FriendList, userID, K)
print("\nTop K Similar Users:", TopK)
print("Recommended Interest Scores:", recommendations)