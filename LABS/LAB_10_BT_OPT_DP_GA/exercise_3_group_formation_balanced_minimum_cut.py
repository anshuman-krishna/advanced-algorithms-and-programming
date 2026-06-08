import random
import math


def count_cross_edges(groupA, groupB, graph):

    cross_edges = 0

    setA = set(groupA)
    setB = set(groupB)

    for u in graph:
        for v in graph[u]:

            # Avoid counting same edge twice
            if u < v:

                if ((u in setA and v in setB) or
                    (u in setB and v in setA)):

                    cross_edges += 1

    return cross_edges



def find_balanced_partition_greedy(graph):

    users = list(graph.keys())

    n = len(users)

    min_size = math.ceil(0.4 * n)

    # Random initial split
    random.shuffle(users)

    mid = n // 2

    groupA = users[:mid]
    groupB = users[mid:]

    improved = True

    while improved:

        improved = False

        current_cross = count_cross_edges(groupA, groupB, graph)

        # Move from A to B
        for u in groupA[:]:

            if len(groupA) - 1 >= min_size:

                groupA.remove(u)
                groupB.append(u)

                new_cross = count_cross_edges(groupA, groupB, graph)

                if new_cross < current_cross:

                    current_cross = new_cross
                    improved = True

                else:
                    # Undo move
                    groupB.remove(u)
                    groupA.append(u)

        # Move from B to A
        for u in groupB[:]:

            if len(groupB) - 1 >= min_size:

                groupB.remove(u)
                groupA.append(u)

                new_cross = count_cross_edges(groupA, groupB, graph)

                if new_cross < current_cross:

                    current_cross = new_cross
                    improved = True

                else:
                    # Undo move
                    groupA.remove(u)
                    groupB.append(u)

    return current_cross, groupA, groupB




def find_balanced_partition_local_search(graph, iterations):

    best_cross = float('inf')

    best_groupA = []
    best_groupB = []

    for i in range(iterations):

        cross, groupA, groupB = find_balanced_partition_greedy(graph)

        if cross < best_cross:

            best_cross = cross
            best_groupA = groupA.copy()
            best_groupB = groupB.copy()

    return best_cross, best_groupA, best_groupB




graph = {
    1: [2, 3],
    2: [1, 3, 4],
    3: [1, 2, 5],
    4: [2, 5],
    5: [3, 4]
}


iterations = 10

cross_edges, groupA, groupB = find_balanced_partition_local_search(
    graph,
    iterations
)

print("Minimum Cross Edges:", cross_edges)
print("Group A:", groupA)
print("Group B:", groupB)