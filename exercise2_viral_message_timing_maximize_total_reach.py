def maximize_reach_exact(budget, costs, reaches):
    n = len(costs)
    dp = [[0 for _ in range(budget + 1)]
          for _ in range(n + 1)]
    for i in range(1, n + 1):
        for b in range(budget + 1):
            dp[i][b] = dp[i - 1][b]
            if costs[i - 1] <= b:
                candidate = (
                    reaches[i - 1]
                    + dp[i - 1][b - costs[i - 1]]
                )
                dp[i][b] = max(dp[i][b], candidate)
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
    return total_cost <= budget

def maximize_reach_greedy(budget, costs, reaches):
    n = len(costs)
    users = []
    for i in range(n):
        ratio = reaches[i] / costs[i]
        users.append((ratio, i))
    users.sort(reverse=True)
    selected_users = []
    total_cost = 0
    total_reach = 0
    for ratio, i in users:
        if total_cost + costs[i] <= budget:
            selected_users.append(i)
            total_cost += costs[i]
            total_reach += reaches[i]
    return total_reach, selected_users

def print_solution(title, reach, users, costs, reaches):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)
    print("Selected Users:", users)
    total_cost = sum(costs[i] for i in users)
    print("Total Cost:", total_cost)
    print("Total Reach:", reach)
    print("\nSelected User Details")
    for i in users:
        print(
            f"User {i} -> Cost = {costs[i]}, "
            f"Reach = {reaches[i]}"
        )

if __name__ == "__main__":
    n = int(input("Enter number of users: "))
    costs = []
    reaches = []
    for i in range(n):
        print(f"\nUser {i}")
        cost = int(input("Enter cost: "))
        reach = int(input("Enter reach: "))
        costs.append(cost)
        reaches.append(reach)
    budget = int(input("\nEnter total budget: "))
    exact_reach, exact_users = maximize_reach_exact(
        budget,
        costs,
        reaches
    )
    greedy_reach, greedy_users = maximize_reach_greedy(
        budget,
        costs,
        reaches
    )
    print_solution(
        "Exact Dynamic Programming Solution",
        exact_reach,
        exact_users,
        costs,
        reaches
    )
    print_solution(
        "Greedy Approximation Solution",
        greedy_reach,
        greedy_users,
        costs,
        reaches
    )
    print("\nBudget Validation")
    print(
        "Exact Solution Within Budget:",
        is_within_budget(exact_users, costs, budget)
    )
    print(
        "Greedy Solution Within Budget:",
        is_within_budget(greedy_users, costs, budget)
    )