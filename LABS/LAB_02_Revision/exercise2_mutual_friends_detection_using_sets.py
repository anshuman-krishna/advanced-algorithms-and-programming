def intersection(set1, set2):
    result = set()
    for element in set1:
        if element in set2:
            result.add(element)
    return result

def difference(set1, set2):
    result = set()
    for element in set1:
        if element not in set2:
            result.add(element)
    return result

def union(set1, set2):
    result = set()
    for element in set1:
        result.add(element)
    for element in set2:
        if element not in result:
            result.add(element)
    return result

def jaccard_similarity(set1, set2):
    inter = intersection(set1, set2)
    uni = union(set1, set2)
    
    inter_size = len(inter)
    uni_size = len(uni)
    
    if uni_size == 0:
        return 0.0
        
    return inter_size / uni_size

def suggest_friends(user_friends, all_users_friends, current_user_id):
    suggestions = set()
    for friend_id in user_friends:
        friends_of_friend = all_users_friends.get(friend_id, set())
        
        for candidate in friends_of_friend:
            if candidate not in user_friends and candidate != current_user_id:
                suggestions.add(candidate)
    return suggestions

# 1. normal case
user_A = {101, 102, 103, 104, 105}
user_B = {103, 104, 106, 107, 108}
print(f"Mutual: {intersection(user_A, user_B)}")
print(f"Jaccard: {jaccard_similarity(user_A, user_B)}")

# 2. edge case, no mutual
no_overlap_A = {1, 2, 3}
no_overlap_B = {4, 5, 6}
print(f"No Mutual Jaccard: {jaccard_similarity(no_overlap_A, no_overlap_B)}")

# 3. edge case, identical list
identical_A = {1, 2}
identical_B = {1, 2}
print(f"Identical Jaccard: {jaccard_similarity(identical_A, identical_B)}")

# 4. edge case, empty sets
empty_A = set()
empty_B = set()
print(f"Empty Set Jaccard: {jaccard_similarity(empty_A, empty_B)}")

# 5. suggestions
global_network = {
    1: {2, 3},
    2: {1, 4, 5},
    3: {1, 5, 6}
}
print(f"Suggestions for User 1: {suggest_friends(global_network[1], global_network, 1)}")