import random
import time
import tkinter as tk
from tkinter import messagebox
from player import Player
from scoring import Scoring
from solver import Solver
from factory import GameEntityFactory


class KRsweeper:

    def __init__(self, root):
        self.root = root
        self.root.title("KRsweeper")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._player, self._scoring, self._solver = GameEntityFactory.create_all()

        self._entities = [self._player, self._scoring, self._solver]

        self.start_time = None
        self._current_preset = None 
        self._first_click = True 
        self._cheated = False 

        self.color_map = {
            1: "blue", 2: "green", 3: "red", 4: "darkblue",
            5: "brown", 6: "cyan", 7: "black", 8: "gray"
        }

        self.n = 0
        self.m = 0
        self._mine_amount = 0
        self._grid = []
        self._visible = []
        self._flags = []
        self.buttons = []
        self._playing = False
        self.menu_frame = tk.Frame(root)
        self.custom_frame = tk.Frame(root)
        self.game_frame = tk.Frame(root)

        self.timer_label = tk.Label(root, text="Time: 00:00:000", font=("Arial", 12))
        self.timer_label.pack()

        self.status_label = tk.Label(root, text="", font=("Arial", 14))
        self.status_label.pack(pady=5)

        self._build_menu()
        self._build_custom_form()
        self.menu_frame.pack()

    def _build_menu(self):
        tk.Label(self.menu_frame, text="KRsweeper 💣", font=("Arial", 18, "bold")).pack(pady=(20, 10))

        for preset_name, cfg in Scoring.PRESETS.items():
            label = f"{preset_name}  ({cfg['rows']}×{cfg['cols']}, {cfg['mines']} mines)"
            tk.Button(
                self.menu_frame, text=label, width=30,
                command=lambda p=preset_name: self._select_preset(p)
            ).pack(pady=4)

        tk.Button(
            self.menu_frame, text="Custom  (no leaderboard)", width=30,
            command=self._select_custom
        ).pack(pady=(10, 20))

    def _build_custom_form(self):
        tk.Label(self.custom_frame, text="Custom game", font=("Arial", 13, "bold")).pack(pady=(10, 5))
        tk.Label(self.custom_frame, text="Rows").pack()
        self.entry_rows = tk.Entry(self.custom_frame)
        self.entry_rows.pack()
        tk.Label(self.custom_frame, text="Columns").pack(pady=(6, 0))
        self.entry_cols = tk.Entry(self.custom_frame)
        self.entry_cols.pack()
        tk.Label(self.custom_frame, text="Mine amount").pack(pady=(6, 0))
        self.entry_bombs = tk.Entry(self.custom_frame)
        self.entry_bombs.pack()
        tk.Button(self.custom_frame, text="Start", command=self._start_custom).pack(pady=8)
        tk.Button(self.custom_frame, text="← Back", command=self._back_to_menu).pack(pady=(0, 12))

    def _select_preset(self, preset_name):
        cfg = Scoring.PRESETS[preset_name]
        self._current_preset = preset_name
        self.menu_frame.pack_forget()
        self._start_game(cfg["rows"], cfg["cols"], cfg["mines"])

    def _select_custom(self):
        self.menu_frame.pack_forget()
        self.custom_frame.pack()

    def _start_custom(self):
        try:
            rows = int(self.entry_rows.get())
            cols = int(self.entry_cols.get())
            mines = int(self.entry_bombs.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")
            return
        self._current_preset = None
        self.custom_frame.pack_forget()
        self._start_game(rows, cols, mines)

    def _back_to_menu(self):
        self.custom_frame.pack_forget()
        self.menu_frame.pack()

    def _start_game(self, rows, cols, mines):
        self.n = rows
        self.m = cols
        self._mine_amount = mines
        self._first_click = True
        self._playing = True

        self._grid = [[0] * self.m for _ in range(self.n)]
        self._visible = [[None] * self.m for _ in range(self.n)]
        self._flags = [[False] * self.m for _ in range(self.n)]

        self._place_mines(skip_x=None, skip_y=None)

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack()

        self._solver_bar = tk.Frame(self.root)
        self._solver_bar.pack(pady=(4, 0))
        self._overlay_btn = tk.Button(
            self._solver_bar, text="🔍 Show Probabilities",
            command=self._toggle_overlay
        )
        self._overlay_btn.pack(side="left", padx=6)
        tk.Button(
            self._solver_bar, text="🤖 Let AI Play",
            command=self._ai_step
        ).pack(side="left", padx=6)

        self.buttons = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                btn = tk.Button(
                    self.game_frame, width=4, height=2,
                    bg="lightblue", relief="sunken",
                    command=lambda x=i, y=j: self.clicked(x, y)
                )
                btn.grid(row=i, column=j)
                btn.bind("<Button-3>", lambda e, x=i, y=j: self.flagged(x, y))
                row.append(btn)
            self.buttons.append(row)

        if self._current_preset is None:
            self.status_label.config(text="Custom game — time not saved", fg="gray")
        else:
            self.status_label.config(text="", fg="black")

    def _place_mines(self, skip_x, skip_y):
        """Place mines randomly, avoiding skip_x/skip_y and its neighbours."""
        self._grid = [[0] * self.m for _ in range(self.n)]

        safe = set()
        if skip_x is not None:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = skip_x + dx, skip_y + dy
                    if 0 <= nx < self.n and 0 <= ny < self.m:
                        safe.add((nx, ny))

        placed = 0
        while placed < self._mine_amount:
            x = random.randint(0, self.n - 1)
            y = random.randint(0, self.m - 1)
            if self._grid[x][y] == -1:
                continue
            if (x, y) in safe:
                continue
            self._grid[x][y] = -1
            placed += 1

    def on_closing(self):
        self._playing = False
        self.root.destroy()

    def _start_timer(self):
        self.start_time = time.time()
        self._tick()

    def _tick(self):
        if self._playing and self.start_time:
            elapsed = time.time() - self.start_time
            m = int(elapsed // 60)
            s = int(elapsed % 60)
            ms = int((elapsed * 1000) % 1000)
            self.timer_label.config(text=f"Time: {m:02d}:{s:02d}:{ms:03d}")
            self.root.after(50, self._tick)

    def check_neighbours(self, x, y):
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.n and 0 <= ny < self.m:
                    if self._grid[nx][ny] == -1:
                        count += 1
        return count

    def open(self, x, y):
        if not (0 <= x < self.n and 0 <= y < self.m):
            return
        if self._visible[x][y] is not None:
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
                    args = {"bg": "#d3d3d3", "relief": "sunken", "text": str(val)}
                    if isinstance(val, int) and val > 0:
                        args["fg"] = self.color_map.get(val, "black")
                    elif val == " ":
                        args["text"] = ""
                    self.buttons[i][j].config(**args)

    def clicked(self, x, y):
        if not self._playing:
            return
        if self._flags[x][y]:
            return
        
        if self._first_click:
            self._first_click = False
            self._place_mines(skip_x=x, skip_y=y)
            self._start_timer()

        if self._grid[x][y] == -1:
            self.buttons[x][y].config(text="💣")
            self._player.die()
            self.start_time = None
            statuses = " | ".join(e.get_status() for e in self._entities)
            self.status_label.config(text=f"Loser — {statuses}", fg="red")
            self._playing = False
            return

        self.open(x, y)
        self.update_buttons()
        if self._solver.is_enabled():
            self._draw_overlay()
        if self.win() or self._all_safe_revealed():
            self.handle_win()

    def flagged(self, x, y):
        if self._visible[x][y] is not None:
            return
        self._flags[x][y] = not self._flags[x][y]
        self.buttons[x][y].config(text="🚩" if self._flags[x][y] else "")
        if self.win() or self._all_safe_revealed():
            self.handle_win()

    def win(self):
        for i in range(self.n):
            for j in range(self.m):
                if self._grid[i][j] == -1 and not self._flags[i][j]:
                    return False
                if self._grid[i][j] != -1 and self._flags[i][j]:
                    return False
        return True

    def _all_safe_revealed(self):
        """True when every non-mine cell has been opened — flags not required."""
        for i in range(self.n):
            for j in range(self.m):
                if self._grid[i][j] != -1 and self._visible[i][j] is None:
                    return False
        return True

    def handle_win(self):
        self._playing = False
        elapsed = time.time() - self.start_time
        m = int(elapsed // 60)
        s = int(elapsed % 60)
        ms = int((elapsed * 1000) % 1000)
        self.timer_label.config(text=f"Time: {m:02d}:{s:02d}:{ms:03d}")

        if self._cheated:
            self.status_label.config(text="Winner! (cheated 🤖 — score not saved)", fg="orange")
            self.show_leaderboard()
        elif self._current_preset:
            self.status_label.config(text="WINNER! 🎉", fg="green")
            self.save_score_popup(elapsed)
        else:
            self.status_label.config(text="WINNER! 🎉", fg="green")
            self.show_leaderboard()

    def save_score_popup(self, score):
        popup = tk.Toplevel(self.root)
        popup.title("Save Score")
        tk.Label(popup, text=f"Preset: {self._current_preset}\nTime: {score:.3f}s\n\nUsername:").pack(pady=(12, 0))
        name_entry = tk.Entry(popup)
        name_entry.pack()
        tk.Label(popup, text="Password:").pack(pady=(8, 0))
        pw_entry = tk.Entry(popup, show="*")
        pw_entry.pack()

        def submit():
            name = name_entry.get().strip()
            password = pw_entry.get()
            if not name:
                messagebox.showerror("Error", "Username cannot be empty.")
                return
            try:
                is_new_best = self._scoring.save_score(self._current_preset, name, password, score)
                popup.destroy()
                if is_new_best:
                    messagebox.showinfo("Saved!", f"New best for {self._current_preset}!\n\n{name}: {score:.3f}s")
                else:
                    messagebox.showinfo("Not a PB", f"Not your best on {self._current_preset}.\n\n{name}: {score:.3f}s")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            self.show_leaderboard()

        tk.Button(popup, text="Save", command=submit).pack(pady=10)
        tk.Button(popup, text="Skip", command=lambda: [popup.destroy(), self.show_leaderboard()]).pack(pady=(0, 12))

    def show_leaderboard(self):
        board = tk.Toplevel(self.root)
        board.title("Leaderboard")
        tk.Label(board, text="🏆 Leaderboard", font=("Arial", 14, "bold")).pack(pady=(12, 5))

        notebook_frame = tk.Frame(board)
        notebook_frame.pack(padx=20, pady=5)

        for preset_name in Scoring.PRESETS:
            tk.Label(notebook_frame, text=preset_name, font=("Arial", 11, "bold")).pack(anchor="w", pady=(8, 0))
            table = tk.Frame(notebook_frame)
            table.pack(anchor="w")

            tk.Label(table, text="#",         width=4,  anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=0)
            tk.Label(table, text="Name",      width=16, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=1)
            tk.Label(table, text="Best Time", width=12, anchor="w", font=("Arial", 10, "bold")).grid(row=0, column=2)

            entries = self._scoring.get_leaderboard(preset_name)
            if not entries:
                tk.Label(table, text="— no scores yet —", fg="gray").grid(row=1, column=0, columnspan=3, sticky="w")
            else:
                for rank, (name, best) in enumerate(entries, start=1):
                    mm = int(best // 60)
                    ss = int(best % 60)
                    ms = int((best * 1000) % 1000)
                    tk.Label(table, text=str(rank),              width=4,  anchor="w").grid(row=rank, column=0)
                    tk.Label(table, text=name,                   width=16, anchor="w").grid(row=rank, column=1)
                    tk.Label(table, text=f"{mm:02d}:{ss:02d}:{ms:03d}", width=12, anchor="w").grid(row=rank, column=2)

        def close_and_reset():
            board.destroy()
            self.reset_game()

        tk.Button(board, text="Play Again", command=close_and_reset).pack(pady=(12, 2))
        tk.Button(board, text="Close",      command=board.destroy).pack(pady=(0, 12))

    def _toggle_overlay(self):
        self._cheated = True
        self._solver.toggle()
        if self._solver.is_enabled():
            self._overlay_btn.config(text="❌ Hide Probabilities")
            self._draw_overlay()
        else:
            self._overlay_btn.config(text="🔍 Show Probabilities")
            self._clear_overlay()

    def _draw_overlay(self):
        if not self._playing or self._first_click:
            return
        probs = self._solver.calculate_probabilities(
            self.n, self.m, self._grid, self._visible, self._flags
        )
        for i in range(self.n):
            for j in range(self.m):
                p = probs[i][j]
                if p < 0:
                    continue
                r = int(255 * p)
                g = int(255 * (1 - p))
                color = f"#{r:02x}{g:02x}00"
                pct = f"{p * 100:.0f}%"
                self.buttons[i][j].config(bg=color, text=pct, fg="white")

    def _clear_overlay(self):
        for i in range(self.n):
            for j in range(self.m):
                if self._visible[i][j] is None and not self._flags[i][j]:
                    self.buttons[i][j].config(bg="lightblue", text="", fg="black")

    def _ai_step(self):
        if not self._playing:
            return
        self._cheated = True
        if self._first_click:
            cx, cy = self.n // 2, self.m // 2
            self.clicked(cx, cy)
        else:
            move = self._solver.best_move(
                self.n, self.m, self._grid, self._visible, self._flags
            )
            if move:
                self.clicked(move[0], move[1])
        if self._solver.is_enabled():
            self._draw_overlay()

    def reset_game(self):
        for entity in self._entities:
            entity.reset()

        self.game_frame.destroy()
        self.game_frame = tk.Frame(self.root)
        self._solver_bar.destroy()
        self._solver_bar = tk.Frame(self.root)
        self.status_label.config(text="", fg="black")
        self.timer_label.config(text="Time: 00:00:000")
        self._playing = False
        self._cheated = False
        self.start_time = None
        self.menu_frame.pack()


root = tk.Tk()
game = KRsweeper(root)
root.mainloop()