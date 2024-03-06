import sys
import os
from PIL import Image, ImageDraw

class Node:
    def __init__(self, state, action, parent):
        self.state = state
        self.action = action
        self.parent = parent

class StackFrontier:
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception('frontier is empty')
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class Queue(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception('frontier is empty')
        else: 
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze:
    def __init__(self, file):
        with open(file) as f:
            content = f.read()
        if content.count('A') != 1:
            raise Exception('Maze must have a starting point')
        if content.count('B') != 1:
            raise Exception('Maze must have an ending point')
        content = content.splitlines()
        self.height = len(content)
        self.width = max(len(line) for line in content)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if content[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif content[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif content[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)
        self.solution = None

    def prints(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("^", end='')
                elif (i, j) == self.start:
                    print('A', end='')
                elif (i, j) == self.goal:
                    print('B', end='')
                elif solution is not None and (i, j) in solution:
                    print('*', end='')
                else:
                    print(' ', end='')
            print()

    

    def neighbors(self, state):
        row, col = state
        candidates = [
        ("up", (row - 1, col)),
        ("down", (row + 1, col)),
        ("left", (row, col - 1)),
        ("right", (row, col + 1))
        ]
        result = []
        for action, (r, c) in candidates:
            try:
                if not self.walls[r][c] and (r, c) not in self.explored:
                        result.append((action, (r, c)))
            except IndexError:
                continue
        return result
    def solve(self):
        self.num_explored = 0
        start = Node(state=self.start, action=None, parent=None)
        frontier = StackFrontier()
        frontier.add(start)
        self.explored = set()
        while True:
            if frontier.empty():
                raise Exception("no solution available")
            node = frontier.remove()
            self.num_explored += 1
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            self.explored.add(node.state)
            for action, state in self.neighbors(node.state):
                if state not in self.explored and not frontier.contains_state(state):
                    child = Node(state=state, action=action, parent=node)
                    frontier.add(child)


    def output_image(self, file, show_soln=True, show_explored=False):
        cell_size = 50
        img_width = self.width * cell_size
        img_height = self.height * cell_size
        img = Image.new("RGB", (img_width, img_height), "black")
        draw = ImageDraw.Draw(img)

        for i in range(self.height):
            for j in range(self.width):
                if self.walls[i][j]:
                    draw.rectangle(
                        [(j * cell_size, i * cell_size), ((j + 1) * cell_size, (i + 1) * cell_size)],
                        fill="gray"  # Use dim gray for walls
                )
                elif (i, j) == self.start:
                    draw.rectangle(
                        [(j * cell_size, i * cell_size), ((j + 1) * cell_size, (i + 1) * cell_size)],
                        fill="green"  # Use light green for start
                )
                elif (i, j) == self.goal:
                    draw.rectangle(
                        [(j * cell_size, i * cell_size), ((j + 1) * cell_size, (i + 1) * cell_size)],
                        fill="red"  # Use light coral for goal
                )
                elif show_soln and self.solution and (i, j) in self.solution[1]:
                    draw.rectangle(
                        [(j * cell_size, i * cell_size), ((j + 1) * cell_size, (i + 1) * cell_size)],
                        fill="gold"  # Use gold for solution path
                )
                elif show_explored and (i, j) in self.explored:
                    draw.rectangle(
                        [(j * cell_size, i * cell_size), ((j + 1) * cell_size, (i + 1) * cell_size)],
                        fill="yellow"  # Use light blue for explored nodes
                )

        img.save(file)

# Example usage:
m = Maze("maze.txt")
try:
    m.solve()
    print("Solution found!")
    print('States explored are: ', m.num_explored)
    m.output_image("maze_solution.png", show_explored=True)
    os.startfile("maze_solution.png")
except Exception as e:
    print(e)
    print("No solution found.")
