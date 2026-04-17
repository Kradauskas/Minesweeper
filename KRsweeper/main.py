import random
import time
import json
import os
import tkinter as tk
from tkinter import messagebox
from player import Player

class KRsweeper:

    def __init__(self, root):
        self.root = root
        self.root.title("KRsweeper")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._player = None

        self.start_time = None
        self.scores_file = "scores.json"

        self.color_map = {
            1: "blue",
            2: "green",
            3: "red",
            4: "darkblue",
            5: "brown",
            6: "cyan",
            7: "black",
            8: "gray"
        }
        self.n = 0
        self.m = 0
        self._grid = []
        self._visible = []
        self._flags = []
        self.buttons = []
        self._playing = True

        self.start_frame = tk.Frame(root)
        self.start_frame.pack()
        self.game_frame = tk.Frame(root)
        
        self.timer_label = tk.Label(root, text="Time: 00:00:000", font=("Arial", 12))
        self.timer_label.pack()

        self.status_label = tk.Label(root, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

        tk.Label(self.start_frame, text="Rows").pack(pady=(10, 0))
        self.entry_rows = tk.Entry(self.start_frame)
        self.entry_rows.pack()

        tk.Label(self.start_frame, text="Collumns").pack(pady=(10, 0))
        self.entry_cols = tk.Entry(self.start_frame)
        self.entry_cols.pack()

        tk.Label(self.start_frame, text="Mine amount").pack(pady=(10, 0))
        self.entry_bombs = tk.Entry(self.start_frame)
        self.entry_bombs.pack()

        tk.Button(self.start_frame, text="Start", command=self.start).pack(pady=20)

    def on_closing(self):
        self._playing = False
        self.root.destroy()

    def update_timer(self):
        if self._playing and self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed * 1000) % 1000)
            self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}:{milliseconds:03d}")
            self.root.after(50, self.update_timer)

    def start(self):
        self.n = int(self.entry_rows.get())
        self.m = int(self.entry_cols.get())
        mine_amount = int(self.entry_bombs.get())
        self.start_time = time.time()

        self.start_frame.pack_forget()
        self.game_frame.pack()
        self.update_timer()

        self._grid = [[0 for _ in range(self.m)] for _ in range(self.n)]
        self._visible = [[None for _ in range(self.m)] for _ in range(self.n)]
        self._flags = [[False for _ in range(self.m)] for _ in range(self.n)]

        for _ in range(mine_amount):
            x = random.randint(0, self.n - 1)
            y = random.randint(0, self.m - 1)
            while self._grid[x][y] == -1:
                x = random.randint(0, self.n - 1)
                y = random.randint(0, self.m - 1)
            self._grid[x][y] = -1

        self.buttons = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                btn = tk.Button(
                    self.game_frame,
                    width=4,
                    height=2,
                    bg="lightblue",
                    relief="sunken",
                    command=lambda x=i, y=j: self.clicked(x, y)
                )
                btn.grid(row=i, column=j)
                btn.bind("<Button-3>", lambda event, x=i, y=j: self.flagged(x, y))
                row.append(btn)
            self.buttons.append(row)

    def check_neighbours(self, x, y):
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if 0 <= nx < self.n and 0 <= ny < self.m:
                    if self._grid[nx][ny] == -1:
                        count += 1
        return count

    def open(self, x, y):
        if x < 0 or x >= self.n or y < 0 or y >= self.m:
            return
        if self._visible[x][y] != None:
            return
        if self._grid[x][y] == -1:
            return
        count = self.check_neighbours(x, y)
        self._visible[x][y] = " " if count == 0 else count
        if count == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    self.open(x + dx, y + dy)

    def update_buttons(self):
        for i in range(self.n):
            for j in range(self.m):
                val = self._visible[i][j]
                if val is not None:
                    config_args = {"bg": "#d3d3d3", "relief": "sunken", "text": str(val)}
                    if isinstance(val, int) and val > 0:
                        config_args["fg"] = self.color_map.get(val, "black")
                    elif val == " ":
                        config_args["text"] = ""
                    self.buttons[i][j].config(**config_args)

    def clicked(self, x, y):
        if not self._playing:
            return
        if self._flags[x][y]:
            return
        if self._grid[x][y] == -1:
            self.buttons[x][y].config(text="💣")
            self.status_label.config(text="Loser", fg="red")
            self._playing = False
            return
        self.open(x, y)
        self.update_buttons()
        if self.win():
            self.handle_win()

    def flagged(self, x, y):
        if self._visible[x][y] != None:
            return
        self._flags[x][y] = not self._flags[x][y]
        if self._flags[x][y]:
            self.buttons[x][y].config(text="🚩")
        else:
            self.buttons[x][y].config(text="")
        if self.win():
            self.handle_win()

    def handle_win(self):
        self._playing = False
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed * 1000) % 1000)
        self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}:{milliseconds:03d}")
        self.status_label.config(text="WINNER", fg="green")
        self.save_score_popup(elapsed)

    def win(self):
        for i in range(self.n):
            for j in range(self.m):
                if self._grid[i][j] == -1 and not self._flags[i][j]:
                    return False
                if self._grid[i][j] != -1 and self._flags[i][j]:
                    return False
        return True

    def save_score_popup(self, score):
        popup = tk.Toplevel(self.root)
        popup.title("Save Score")
        tk.Label(popup, text=f"Time: {score:.3f}s\n\nEnter Username").pack(pady=(10, 0))
        name_entry = tk.Entry(popup)
        name_entry.pack()
        tk.Label(popup, text="Enter Password").pack(pady=(10, 0))
        pw_entry = tk.Entry(popup, show="*")
        pw_entry.pack()
        def submit():
            self.process_save(score, name_entry.get(), pw_entry.get())
            popup.destroy()
        tk.Button(popup, text="Save", command=submit).pack(pady=20)

    def process_save(self, score, name, password):
        data = {}
        if os.path.exists(self.scores_file):
            with open(self.scores_file, "r") as f:
                data = json.load(f)
        
        if name in data:
            if data[name]["password"] != password:
                messagebox.showerror("Error", "Incorrect password!")
                return
        else:
            data[name] = {"password": password, "best_score": float('inf')}
        
        if score < data[name]["best_score"]:
            data[name]["best_score"] = score
            with open(self.scores_file, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", f"Score saved!\n\nUser: {name}\nTime: {score:.3f}s")

root = tk.Tk()
game = KRsweeper(root)
root.mainloop()