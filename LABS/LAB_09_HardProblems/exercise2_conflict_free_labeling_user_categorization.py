class GraphColoring:
    def __init__(self, graph):
        self.graph = graph
        self.n = len(graph)

    def is_valid_labeling(self, labeling):
        for u in self.graph:
            for v in self.graph[u]:

                if labeling[u] == labeling[v]:
                    return False

        return True
    def can_use_color(self, node, color, labeling):
        for neighbor in self.graph[node]:

            if labeling[neighbor] == color:
                return False
        return True

    def solve(self, node, k, labeling):

        if node == self.n:
            return True

        for color in range(1, k + 1):

            if self.can_use_color(node, color, labeling):

                labeling[node] = color

                if self.solve(node + 1, k, labeling):
                    return True
                labeling[node] = 0

        return False
    def assign_labels(self, k):
        labeling = [0] * self.n
        success = self.solve(0, k, labeling)
        return success, labeling

    def find_min_labels(self):
        for k in range(1, self.n + 1):
            success, labeling = self.assign_labels(k)
            if success:
                return k, labeling
        return None


def create_graph():
    graph = {}
    n = int(input("Enter number of users/nodes: "))
    for i in range(n):
        graph[i] = []
    e = int(input("Enter number of connections/edges: "))
    print("\nEnter edges (u v):")
    for _ in range(e):
        u, v = map(int, input().split())
        graph[u].append(v)
        graph[v].append(u)
    return graph


def main():
    print("====================================")
    print(" CONFLICT-FREE LABELING SYSTEM ")
    print("====================================")
    graph = create_graph()
    gc = GraphColoring(graph)
    while True:

        print("\n========== MENU ==========")
        print("1. Check Valid Labeling")
        print("2. Assign Labels with k Colors")
        print("3. Find Minimum Labels")
        print("4. Display Graph")
        print("5. Exit")

        choice = int(input("Enter your choice: "))

        if choice == 1:
            labeling = []
            print("\nEnter labels for each node:")
            for i in range(gc.n):

                label = int(input(f"Label for node {i}: "))
                labeling.append(label)
            if gc.is_valid_labeling(labeling):

                print("\nVALID labeling")
                print("No conflicts found")
            else:

                print("\nINVALID labeling")
                print("Conflict exists")

        elif choice == 2:

            k = int(input("\nEnter maximum number of labels/colors: "))

            success, labeling = gc.assign_labels(k)

            if success:
                print("\nSUCCESS")
                print("Valid labeling found")

                for i in range(gc.n):
                    print(f"Node {i} ---> Label {labeling[i]}")
            else:
                print("\nFAILED")
                print("Cannot color graph with", k, "labels")

        elif choice == 3:

            min_k, labeling = gc.find_min_labels()

            print("\nMinimum labels required:", min_k)

            print("\nOptimal Labeling:")

            for i in range(gc.n):
                print(f"Node {i} ---> Label {labeling[i]}")

        elif choice == 4:

            print("\nGraph Representation:")

            for node in graph:
                print(f"{node} ---> {graph[node]}")


        elif choice == 5:

            print("\nProgram Ended")
            break

        else:

            print("\nInvalid choice")



if __name__ == "__main__":
    main()