# ---------------------------------------------------------
# Project: Pathfinding Visualizer
# Author: Abeer (FAST University)
# Description: Visualizing BFS, DFS, UCS, DLS, IDDFS, and Bidirectional Search
# GitHub: github.com/abeerashraf1405
# © 2026 Abeer - All Rights Reserved
# ---------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import collections
import heapq
import time

# --- Configuration Constants ---
ROWS, COLS = 10, 10
CELL_SIZE = 50
DELAY = 0.05
COLORS = {
    "empty": "white",
    "wall": "#2c3e50", # Darker slate for walls
    "start": "#f39c12", # Orange
    "target": "#e74c3c", # Red
    "frontier": "#9b59b6", # Purple
    "visited": "#3498db", # Blue
    "path": "#2ecc71",   # Green
    "target_frontier": "#ff00ff" # Magenta for bidirectional
}

GRID_MAP = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

START_POS = (5, 7)
TARGET_POS = (6, 1)

class PathfinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Path Finder Visualizer")
        self.rects = {}
        self.setup_ui()
        self.reset_grid()

    def setup_ui(self):
        # Top Control Panel
        control_frame = tk.Frame(self.root, bg="#ecf0f1", padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(control_frame, text="Algorithm:", bg="#ecf0f1", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.algo_var = tk.StringVar()
        self.algo_combo = ttk.Combobox(control_frame, textvariable=self.algo_var, state="readonly")
        self.algo_combo['values'] = ("BFS", "DFS", "UCS", "DLS", "IDDFS", "Bidirectional")
        self.algo_combo.current(0)
        self.algo_combo.pack(side=tk.LEFT, padx=10)

        tk.Button(control_frame, text="▶ Run", command=self.run_search, bg="#2ecc71", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="⟳ Reset", command=self.reset_grid, bg="#95a5a6", fg="white", width=10).pack(side=tk.LEFT)

        # Main Canvas
        self.canvas = tk.Canvas(self.root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg="white", highlightthickness=0)
        self.canvas.pack(pady=20, padx=20)

        # Status Bar
        self.status_var = tk.StringVar(value="Select an algorithm and click Run")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def reset_grid(self):
        self.canvas.delete("all")
        self.rects = {}
        for r in range(ROWS):
            for c in range(COLS):
                color = COLORS["empty"]
                if GRID_MAP[r][c] == -1: color = COLORS["wall"]
                elif (r, c) == START_POS: color = COLORS["start"]
                elif (r, c) == TARGET_POS: color = COLORS["target"]
                
                rect = self.canvas.create_rectangle(
                    c*CELL_SIZE, r*CELL_SIZE, (c+1)*CELL_SIZE, (r+1)*CELL_SIZE, 
                    fill=color, outline="#bdc3c7"
                )
                self.rects[(r, c)] = rect
                if (r, c) == START_POS: self.canvas.create_text(c*CELL_SIZE+25, r*CELL_SIZE+25, text="S")
                if (r, c) == TARGET_POS: self.canvas.create_text(c*CELL_SIZE+25, r*CELL_SIZE+25, text="T")
        self.status_var.set("Ready.")

    def update_cell(self, node, color_key):
        if node in [START_POS, TARGET_POS]: return
        self.canvas.itemconfig(self.rects[node], fill=COLORS.get(color_key, color_key))
        self.root.update()

    def get_neighbors(self, node):
        r, c = node
        # Standard 4-way + Diagonals (optional, kept your logic mostly)
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        res = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and GRID_MAP[nr][nc] != -1:
                res.append((nr, nc))
        return res

    # --- Search Logic ---
    def run_search(self):
        algo = self.algo_var.get()
        self.reset_grid()
        self.status_var.set(f"Running {algo}...")
        
        path = None
        if algo == "BFS": path = self.bfs()
        elif algo == "DFS": path = self.dfs()
        elif algo == "UCS": path = self.ucs()
        elif algo == "DLS": path = self.dls(15)
        elif algo == "IDDFS": path = self.iddfs(20)
        elif algo == "Bidirectional": path = self.bidirectional()

        if path:
            self.status_var.set(f"Success! Path length: {len(path)}")
            for node in path:
                self.update_cell(node, "path")
                time.sleep(0.02)
        else:
            self.status_var.set("No path found.")

    def bfs(self):
        queue = collections.deque([START_POS])
        parent = {START_POS: None}
        while queue:
            curr = queue.popleft()
            if curr == TARGET_POS: return self.reconstruct(parent, curr)
            self.update_cell(curr, "visited")
            time.sleep(DELAY)
            for n in self.get_neighbors(curr):
                if n not in parent:
                    parent[n] = curr
                    queue.append(n)
                    self.update_cell(n, "frontier")
        return None

    def dfs(self):
        stack = [START_POS]
        visited = {START_POS}
        parent = {START_POS: None}
        while stack:
            curr = stack.pop()
            if curr == TARGET_POS: return self.reconstruct(parent, curr)
            self.update_cell(curr, "visited")
            time.sleep(DELAY)
            for n in self.get_neighbors(curr):
                if n not in visited:
                    visited.add(n)
                    parent[n] = curr
                    stack.append(n)
                    self.update_cell(n, "frontier")
        return None

    def ucs(self):
        pq = [(0, START_POS)]
        parent = {START_POS: None}
        costs = {START_POS: 0}
        while pq:
            c_cost, curr = heapq.heappop(pq)
            if curr == TARGET_POS: return self.reconstruct(parent, curr)
            self.update_cell(curr, "visited")
            time.sleep(DELAY)
            for n in self.get_neighbors(curr):
                new_cost = c_cost + 1
                if n not in costs or new_cost < costs[n]:
                    costs[n] = new_cost
                    parent[n] = curr
                    heapq.heappush(pq, (new_cost, n))
                    self.update_cell(n, "frontier")
        return None

    def dls(self, limit, start_node=START_POS):
        # Using a local parent map and depth tracker for this specific limit run
        stack = [(start_node, 0)]
        parent = {start_node: None}
        visited_depths = {start_node: 0} # Track the shallowest depth we reached a node

        while stack:
            curr, d = stack.pop()

            if curr == TARGET_POS:
                return self.reconstruct(parent, curr)

            if d < limit:
                for n in self.get_neighbors(curr):
                    # Only visit if not seen OR if seen at a deeper level (found a shortcut)
                    if n not in visited_depths or d + 1 < visited_depths[n]:
                        visited_depths[n] = d + 1
                        parent[n] = curr
                        stack.append((n, d + 1))
                        
                        self.update_cell(n, "frontier")
            
            self.update_cell(curr, "visited")
            # Small sleep to prevent UI freezing during the deep recursion
            time.sleep(0.001) 
            
        return None

    def iddfs(self, max_d):
        for d in range(1, max_d + 1):
            self.status_var.set(f"IDDFS: Searching depth {d}...")
            # Clean grid visuals for each new depth iteration
            self.reset_grid() 
            res = self.dls(d)
            if res: 
                return res
        return None

    def bidirectional(self):
        q_s, q_t = collections.deque([START_POS]), collections.deque([TARGET_POS])
        p_s, p_t = {START_POS: None}, {TARGET_POS: None}
        while q_s and q_t:
            # Forward step
            curr_s = q_s.popleft()
            self.update_cell(curr_s, "visited")
            if curr_s in p_t: return self.merge(curr_s, p_s, p_t)
            for n in self.get_neighbors(curr_s):
                if n not in p_s:
                    p_s[n] = curr_s
                    q_s.append(n)
                    self.update_cell(n, "frontier")
            # Backward step
            curr_t = q_t.popleft()
            self.update_cell(curr_t, "visited") # Blue-ish
            if curr_t in p_s: return self.merge(curr_t, p_s, p_t)
            for n in self.get_neighbors(curr_t):
                if n not in p_t:
                    p_t[n] = curr_t
                    q_t.append(n)
                    self.update_cell(n, "target_frontier")
            time.sleep(DELAY)
        return None

    def reconstruct(self, parent, curr):
        path = []
        while curr:
            path.append(curr)
            curr = parent.get(curr)
        return path[::-1]

    def merge(self, meet, p_s, p_t):
        path_s = self.reconstruct(p_s, meet)
        path_t = []
        curr = p_t.get(meet)
        while curr:
            path_t.append(curr)
            curr = p_t.get(curr)
        return path_s + path_t

if __name__ == "__main__":
    root = tk.Tk()
    app = PathfinderApp(root)
    root.mainloop()