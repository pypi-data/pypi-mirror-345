def first(sub):
    if sub==1:
        print("""
graph = { 
'5': ['3', '7'],
'3': ['2', '4'],
'7': ['8'],
'2':[],
'4': ['8'],
'8': [] 
} 
visited = set() 
def dfs(visited, graph, node): 
    if node not in visited: 
        print(node) 
        visited.add(node) 
        for neighbour in graph[node]: 
                dfs(visited, graph, neighbour) 
print("Following is the Depth-First Search:") 
dfs(visited, graph, '5') 
""")
    else:
        print("""
graph = { 
'5': ['3', '7'],
'3': ['2', '4'],
'7': ['8'],
'2':[],
'4': ['8'],
'8': [] 
} 
visited = [] 
queue = [] 
def bfs(visited, graph, node): 
    visited.append(node) 
    queue.append(node) 
    while queue: 
        m = queue.pop(0) 
        print(m, end=" ") 
        for neighbour in graph[m]: 
            if neighbour not in visited: 
                visited.append(neighbour) 
                queue.append(neighbour) 
print("Following is the Breadth-First Search:") 
bfs(visited, graph, '5')
""")
    
def second():
    print("""
def aStarAlgo(start_node, stop_node):
    open_set = set([start_node])
    closed_set = set()
    g = {}
    parents = {}

    g[start_node] = 0
    parents[start_node] = start_node

    while len(open_set) > 0:
        n = None

        for v in open_set:
            if n is None or g[v] + heuristic(v) < g[n] + heuristic(n):
                n = v

        if n is None:
            print('Path does not exist!')
            return None

        if n == stop_node:
            path = []
            while parents[n] != n:
                path.append(n)
                n = parents[n]
            path.append(start_node)
            path.reverse()
            print('Path found: {}'.format(path))
            return path

        for (m, weight) in get_neighbors(n):
            if m not in open_set and m not in closed_set:
                open_set.add(m)
                parents[m] = n
                g[m] = g[n] + weight
            else:
                if g[m] > g[n] + weight:
                    g[m] = g[n] + weight
                    parents[m] = n
                    if m in closed_set:
                        closed_set.remove(m)
                        open_set.add(m)

        open_set.remove(n)
        closed_set.add(n)

    print('Path does not exist!')
    return None


def get_neighbors(v):
    if v in Graph_nodes:
        return Graph_nodes[v]
    else:
        return None


def heuristic(n):
    H_dist = {
        'A': 11,
        'B': 6,
        'C': 99,
        'D': 1,
        'E': 7,
        'G': 0,
    }
    return H_dist[n]


Graph_nodes = {
    'A': [('B', 2), ('E', 3)],
    'B': [('A', 2), ('C', 1), ('G', 9)],
    'C': [('B', 1)],
    'D': [('E', 6), ('G', 1)],
    'E': [('A', 3), ('D', 6)],
    'G': [('B', 9), ('D', 1)]
}

aStarAlgo('A', 'G')
""")
    
def third(sub):
    if sub==1:
        print("""
def selectionSort(array, size):
    for ind in range(size):
        min_index = ind
        for j in range(ind + 1, size):
            if array[j] < array[min_index]:
                min_index = j
        (array[ind], array[min_index]) = (array[min_index], array[ind])

arr = [-2, 45, 0, 11, -9, 88, -97, -202, 747]
size = len(arr)
selectionSort(arr, size)
print('The array after sorting in Ascending Order by selection sort is:')
print(arr)

""")
    elif sub==2:
        print("""
# Prim's Algorithm
import sys

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)] for row in range(vertices)]

    def printMST(self, parent):
        print("Edge \tWeight")
        for i in range(1, self.V):
            print(parent[i], "-", i, "\t", self.graph[i][parent[i]])

    def minKey(self, key, mstSet):
        min_val = sys.maxsize
        min_index = -1
        for v in range(self.V):
            if key[v] < min_val and not mstSet[v]:
                min_val = key[v]
                min_index = v
        return min_index

    def primMST(self):
        key = [sys.maxsize] * self.V
        parent = [None] * self.V
        key[0] = 0
        mstSet = [False] * self.V
        parent[0] = -1

        for cout in range(self.V):
            u = self.minKey(key, mstSet)
            mstSet[u] = True
            for v in range(self.V):
                if self.graph[u][v] > 0 and not mstSet[v] and key[v] > self.graph[u][v]:
                    key[v] = self.graph[u][v]
                    parent[v] = u

        self.printMST(parent)

if __name__ == '__main__':
    g = Graph(5)
    g.graph = [
        [0, 2, 0, 6, 0],
        [2, 0, 3, 8, 5],
        [0, 3, 0, 0, 7],
        [6, 8, 0, 0, 9],
        [0, 5, 7, 9, 0]
    ]
    g.primMST()
""")
    elif sub==3:
        print("""
# Dijkstra's Algorithm
class Graph():
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)] for row in range(vertices)]

    def printSolution(self, dist):
        print("Vertex \t Distance from Source")
        for node in range(self.V):
            print(node, "\t", dist[node])

    def minDistance(self, dist, sptSet):
        min_val = sys.maxsize
        min_index = -1
        for v in range(self.V):
            if dist[v] < min_val and not sptSet[v]:
                min_val = dist[v]
                min_index = v
        return min_index

    def dijkstra(self, src):
        dist = [sys.maxsize] * self.V
        dist[src] = 0
        sptSet = [False] * self.V

        for cout in range(self.V):
            u = self.minDistance(dist, sptSet)
            sptSet[u] = True
            for v in range(self.V):
                if (self.graph[u][v] > 0 and not sptSet[v] and
                        dist[v] > dist[u] + self.graph[u][v]):
                    dist[v] = dist[u] + self.graph[u][v]

        self.printSolution(dist)
g = Graph(9)
g.graph = [
    [0, 4, 0, 0, 0, 0, 0, 8, 0],
    [4, 0, 8, 0, 0, 0, 0, 11, 0],
    [0, 8, 0, 7, 0, 4, 0, 0, 2],
    [0, 0, 7, 0, 9, 14, 0, 0, 0],
    [0, 0, 0, 9, 0, 10, 0, 0, 0],
    [0, 0, 4, 14, 10, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 2, 0, 1, 6],
    [8, 11, 0, 0, 0, 0, 1, 0, 7],
    [0, 0, 2, 0, 0, 0, 6, 7, 0]
]
g.dijkstra(0)
""")
    elif sub==4:
        print("""
#Kruskal Algo
class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []

    def addEdge(self, u, v, w):
        self.graph.append([u, v, w])

    def find(self, parent, i):
        if parent[i] != i:
            parent[i] = self.find(parent, parent[i])
        return parent[i]

    def union(self, parent, rank, x, y):
        if rank[x] < rank[y]:
            parent[x] = y
        elif rank[x] > rank[y]:
            parent[y] = x
        else:
            parent[y] = x
            rank[x] += 1

    def KruskalMST(self):
        result = []
        i = 0
        e = 0
        self.graph = sorted(self.graph, key=lambda item: item[2])
        parent = []
        rank = []

        for node in range(self.V):
            parent.append(node)
            rank.append(0)

        while e < self.V - 1:
            u, v, w = self.graph[i]
            i += 1
            x = self.find(parent, u)
            y = self.find(parent, v)

            if x != y:
                e += 1
                result.append([u, v, w])
                self.union(parent, rank, x, y)

        minimumCost = 0
        print("Edges in the constructed MST:")
        for u, v, weight in result:
            minimumCost += weight
            print(f"{u} -- {v} == {weight}")
        print("Minimum Spanning Tree cost:", minimumCost)

if __name__ == '__main__':
    g = Graph(4)
    g.addEdge(0, 1, 10)
    g.addEdge(0, 2, 6)
    g.addEdge(0, 3, 5)
    g.addEdge(1, 3, 15)
    g.addEdge(2, 3, 4)
    g.KruskalMST()
""")
    else:
        print("""
def printJobScheduling(arr, t):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j][2] < arr[j + 1][2]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    result = [False] * t
    job = ['-1'] * t

    for i in range(n):
        for j in range(min(t - 1, arr[i][1] - 1), -1, -1):
            if result[j] is False:
                result[j] = True
                job[j] = arr[i][0]
                break

    print("Following is the maximum profit sequence of jobs:")
    print(" -> ".join(job))

if __name__ == "__main__":
    arr = [['a', 2, 100], ['b', 1, 19], ['c', 2, 27],
           ['d', 1, 25], ['e', 3, 15]]
    printJobScheduling(arr, 3)
""")
    
def fourth(sub):
    if sub==1:
        print("""
N = 4

def printSolution(board):
    for i in range(N):
        for j in range(N):
            print(board[i][j], end=" ")
        print()

def isSafe(board, row, col):
    # Check this row on the left side
    for i in range(col):
        if board[row][i] == 1:
            return False

    # Check upper diagonal on the left side
    for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False

    # Check lower diagonal on the left side
    for i, j in zip(range(row, N, 1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False

    return True

def solveNQUtil(board, col):
    if col >= N:
        return True

    for i in range(N):
        if isSafe(board, i, col):
            board[i][col] = 1
            if solveNQUtil(board, col + 1):
                return True
            board[i][col] = 0

    return False

def solveNQ():
    board = [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]]

    if not solveNQUtil(board, 0):
        print("Solution does not exist")
        return False

    print("One of the possible solutions is:")
    printSolution(board)
    return True

solveNQ()

""")
    else:
        print("""
G = [
    [0, 1, 1, 0, 1, 0],
    [1, 0, 1, 1, 0, 1],
    [1, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 0, 1],
    [1, 0, 1, 0, 0, 1],
    [0, 1, 0, 1, 1, 0]
]

nodes = "abcdef"
node_index = {}

for i in range(len(G)):
    node_index[nodes[i]] = i

degree = []
for i in range(len(G)):
    degree.append(sum(G[i]))

colors = ["Blue", "Red", "Yellow", "Green"]
colorDict = {}

for i in range(len(G)):
    colorDict[nodes[i]] = colors.copy()

sortedNode = []
used_indices = []

for _ in range(len(degree)):
    max_deg = -1
    idx = -1
    for j in range(len(degree)):
        if j not in used_indices and degree[j] > max_deg:
            max_deg = degree[j]
            idx = j
    used_indices.append(idx)
    sortedNode.append(nodes[idx])

theSolution = {}
for n in sortedNode:
    current_color = colorDict[n][0]  
    theSolution[n] = current_color
    # Remove this color from adjacent nodes
    for j in range(len(G[node_index[n]])):
        if G[node_index[n]][j] == 1:
            neighbor = nodes[j]
            if current_color in colorDict[neighbor]:
                colorDict[neighbor].remove(current_color)

print("Node Coloring Result:")
for t in sorted(theSolution):
    print("Node", t, "=", theSolution[t])
""")
    
def fifth():
    print("""

def remind_name():
    print("Please, remind me your name.")
    name = input()
    print("What a great name you have, {}!".format(name))

def guess_age():
    print("Let me guess your age.")
    print("Enter remainders of dividing your age by 3, 5 and 7.")
    rem3 = int(input())
    rem5 = int(input())
    rem7 = int(input())
    age = (rem3 * 70 + rem5 * 21 + rem7 * 15) % 105
    print("Your age is {}; that's a good time to start programming!".format(age))

def count():
    print("Now I will show you that I can count to any number you want.")
    num = int(input())
    for i in range(num + 1):
        print("{}!".format(i))

def test():
    print("Let's test your programming knowledge.")
    print("Why do we use methods?")
    print("1. To repeat a statement multiple times.")
    print("2. To decompose a program into several small subroutines.")
    print("3. To demonstrate the execution of a program.")
    print("4. To interrupt the execution of a program.")
    answer = 2
    while True:
        guess = int(input())
        if guess == answer:
            break
        print("Please, try again.")
    print("Completed, have a nice day!")

def end():
    print("Congratulations, have a nice day!")

print("Hello! My name is SBot.")
print("I was created in 2021.")
remind_name()
guess_age()
count()
test()
end()
""")
    
def sixth():
    print("""
import csv

student_fields = ['roll', 'name', 'age', 'email', 'phone']
student_database = 'students.csv'

def display_menu():
    print("\n------------------------------------")
    print(" Welcome to Student Information System")
    print("------------------------------------")
    print("1. Add New Student")
    print("2. View Students")
    print("3. Search Student")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Quit")

def add_student():
    print("\n--- Add Student Information ---")
    student_data = []
    for field in student_fields:
        value = input("Enter " + field + ": ")
        student_data.append(value)
    with open(student_database, "a", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(student_data)
    print("Data saved successfully!\n")
    input("Press Enter to continue...")

def view_students():
    print("\n--- Student Records ---")
    with open(student_database, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        print("\t".join(student_fields))
        print("-" * 50)
        for row in reader:
            print("\t".join(row))
    input("\nPress Enter to continue...")

def search_student():
    print("\n--- Search Student ---")
    roll = input("Enter roll no. to search: ")
    found = False
    with open(student_database, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0 and row[0] == roll:
                print("\n--- Student Found ---")
                for i in range(len(student_fields)):
                    print(f"{student_fields[i].capitalize()}: {row[i]}")
                found = True
                break
    if not found:
        print("Roll No. not found in our database")
    input("Press Enter to continue...")

def update_student():
    print("\n--- Update Student ---")
    roll = input("Enter roll no. to update: ")
    updated_data = []
    found = False
    with open(student_database, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == roll:
                print("Student Found. Enter new data:")
                updated_row = []
                for field in student_fields:
                    value = input("Enter " + field + ": ")
                    updated_row.append(value)
                updated_data.append(updated_row)
                found = True
            else:
                updated_data.append(row)
    if found:
        with open(student_database, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(updated_data)
        print("Student record updated successfully!")
    else:
        print("Roll No. not found in our database")
    input("Press Enter to continue...")

def delete_student():
    global student_fields
    global student_database
    print("--- Delete Student ---")
    roll = input("Enter roll no. to delete: ")
    student_found = False
    updated_data = []
    with open(student_database, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 0:
                continue  # skip empty rows
            if row[0] != roll:
                updated_data.append(row)
            else:
                student_found = True
    if student_found:
        with open(student_database, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(updated_data)
        print("Roll no.", roll, "deleted successfully")
    else:
        print("Roll No. not found in our database")
    input("Press any key to continue")

while True:
    display_menu()
    choice = input("Enter your choice (1-6): ")
    if choice == '1':
        add_student()
    elif choice == '2':
        view_students()
    elif choice == '3':
        search_student()
    elif choice == '4':
        update_student()
    elif choice == '5':
        delete_student()
    elif choice == '6':
        print("\nThank you for using our system!")
        break
    else:
        print("Invalid choice. Please try again.")
""")