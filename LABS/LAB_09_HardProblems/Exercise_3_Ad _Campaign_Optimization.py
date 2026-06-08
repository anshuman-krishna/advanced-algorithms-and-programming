def maximize_reach(budget, costs, influences):
    n = len(costs)

    # Create DP table
    dp = [[0 for _ in range(budget + 1)] for _ in range(n + 1)]

    # Fill DP table
    for i in range(1, n + 1):
        for b in range(budget + 1):

            if costs[i - 1] <= b:
                include_value = influences[i - 1] + dp[i - 1][b - costs[i - 1]]
                exclude_value = dp[i - 1][b]

                dp[i][b] = max(include_value, exclude_value)

            else:
                dp[i][b] = dp[i - 1][b]

    # Find selected users
    selected_users = []
    b = budget

    for i in range(n, 0, -1):
        if dp[i][b] != dp[i - 1][b]:
            selected_users.append(i - 1)
            b -= costs[i - 1]

    selected_users.reverse()

    return dp[n][budget], selected_users



def is_within_budget(selection, costs, budget):
    total_cost = 0

    for user in selection:
        total_cost += costs[user]

    if total_cost <= budget:
        return True
    else:
        return False




def fast_alternative_strategy(budget, costs, influences):
    n = len(costs)

    ratio_list = []

    # Calculate influence/cost ratio
    for i in range(n):
        ratio = influences[i] / costs[i]
        ratio_list.append((ratio, i))

    # Sort by ratio in descending order
    ratio_list.sort(reverse=True)

    total_cost = 0
    total_influence = 0
    selected_users = []

   
    for ratio, user in ratio_list:

        if total_cost + costs[user] <= budget:
            selected_users.append(user)
            total_cost += costs[user]
            total_influence += influences[user]

    return total_influence, selected_users




budget = 10
costs = [2, 3, 5, 7]
influences = [20, 30, 45, 77]


exact_influence, exact_users = maximize_reach(
    budget,
    costs,
    influences
)

print("Exact Solution")
print("Maximum Influence:", exact_influence)
print("Selected Users:", exact_users)

# Budget Check
print("\nWithin Budget:",
      is_within_budget(exact_users, costs, budget))


greedy_influence, greedy_users = fast_alternative_strategy(
    budget,
    costs,
    influences
)

print("\nGreedy Solution")
print("Total Influence:", greedy_influence)
print("Selected Users:", greedy_users)