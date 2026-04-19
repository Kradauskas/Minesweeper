import time
import tkinter as tk
from tkinter import messagebox
from minesweeper import Minesweeper
from scoring import Scoring


class App:

    COLOR_MAP = {
        1: "blue", 2: "green", 3: "red", 4: "darkblue",
        5: "brown", 6: "cyan", 7: "black", 8: "gray"
    }

    def __init__(self, root):
        self.root = root
        self.root.title("KRsweeper")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._game = Minesweeper()

        hud = tk.Frame(root, pady=6)
        hud.pack(fill="x")
        self._timer_label = tk.Label(hud, text="00:00:000",
                                     font=("Courier", 14, "bold"))
        self._timer_label.pack()
        self._bombs_label = tk.Label(hud, text="", font=("Arial", 11))
        self._bombs_label.pack()

        self._menu_frame = tk.Frame(root)
        self._custom_frame = tk.Frame(root)
        self._game_frame = tk.Frame(root)
        self._solver_bar = tk.Frame(root)
        self._overlay_btn = None
        self._buttons = []

        self._build_menu()
        self._build_custom_form()
        self._menu_frame.pack()

    def _build_menu(self):
        tk.Label(self._menu_frame, text="KRsweeper 💣",
                 font=("Arial", 20, "bold")).pack(pady=(20, 14))

        for name, cfg in Scoring.PRESETS.items():
            label = f"{name}  —  {cfg['rows']}×{cfg['cols']},  {cfg['mines']} mines"
            tk.Button(self._menu_frame, text=label, width=32, pady=4,
                      command=lambda p=name: self._select_preset(p)).pack(pady=3)

        tk.Frame(self._menu_frame, height=1, bg="#cccccc").pack(
            fill="x", padx=30, pady=10)
        tk.Button(self._menu_frame, text="Custom  (no leaderboard)",
                  width=32, pady=4,
                  command=self._select_custom).pack(pady=(0, 20))

    def _build_custom_form(self):
        tk.Label(self._custom_frame, text="Custom Game",
                 font=("Arial", 14, "bold")).pack(pady=(14, 8))

        for label, attr in [("Rows", "_entry_rows"),
                             ("Columns", "_entry_cols"),
                             ("Mines", "_entry_bombs")]:
            tk.Label(self._custom_frame, text=label).pack()
            entry = tk.Entry(self._custom_frame, width=10, justify="center")
            entry.pack(pady=(0, 6))
            setattr(self, attr, entry)

        tk.Button(self._custom_frame, text="Start", width=14,
                  command=self._start_custom).pack(pady=(4, 4))
        tk.Button(self._custom_frame, text="← Back", width=14,
                  command=self._back_to_menu).pack(pady=(0, 14))

    def _select_preset(self, preset_name):
        cfg = Scoring.PRESETS[preset_name]
        self._menu_frame.pack_forget()
        self._start_game(cfg["rows"], cfg["cols"], cfg["mines"], preset_name)

    def _select_custom(self):
        self._menu_frame.pack_forget()
        self._custom_frame.pack()

    def _start_custom(self):
        try:
            rows = int(self._entry_rows.get())
            cols = int(self._entry_cols.get())
            mines = int(self._entry_bombs.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid whole numbers.")
            return

        if rows < 2 or cols < 2:
            messagebox.showerror("Error", "Grid must be at least 2×2.")
            return
        if mines < 1:
            messagebox.showerror("Error", "There must be at least 1 mine.")
            return
        max_mines = rows * cols - 9
        if max_mines < 1:
            max_mines = rows * cols - 1
        if mines > max_mines:
            messagebox.showerror(
                "Error",
                f"Too many mines for this grid.\n"
                f"Maximum for {rows}×{cols} is {max_mines}."
            )
            return

        self._custom_frame.pack_forget()
        self._start_game(rows, cols, mines, preset=None)

    def _back_to_menu(self):
        self._custom_frame.pack_forget()
        self._menu_frame.pack()

    def _start_game(self, rows, cols, mines, preset):
        self._game.new_game(rows, cols, mines, preset)
        self._timer_label.config(text="00:00:000", fg="black")
        self._bombs_label.config(text=f"💣 {self._game.bombs_remaining()}")

        self._game_frame = tk.Frame(self.root)
        self._game_frame.pack()
        self._buttons = []
        for i in range(rows):
            row = []
            for j in range(cols):
                btn = tk.Button(
                    self._game_frame, width=4, height=2,
                    bg="lightblue", relief="raised",
                    command=lambda x=i, y=j: self._on_click(x, y)
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind("<Button-3>", lambda e, x=i, y=j: self._on_flag(x, y))
                row.append(btn)
            self._buttons.append(row)

        self._solver_bar = tk.Frame(self.root)
        self._solver_bar.pack(pady=(6, 2))
        self._overlay_btn = tk.Button(self._solver_bar, text="🔍 Probabilities",
                                      command=self._toggle_overlay)
        self._overlay_btn.pack(side="left", padx=6)
        tk.Button(self._solver_bar, text="🤖 AI Play",
                  command=self._ai_step).pack(side="left", padx=6)

        self._tick()

    def _tick(self):
        if not self._game.playing:
            return
        if self._game.start_time:
            elapsed = time.time() - self._game.start_time
            m = int(elapsed // 60)
            s = int(elapsed % 60)
            ms = int((elapsed * 1000) % 1000)
            self._timer_label.config(text=f"{m:02d}:{s:02d}:{ms:03d}")
        self.root.after(50, self._tick)

    def _on_click(self, x, y):
        result = self._game.click(x, y)
        if result == "explode":
            self._buttons[x][y].config(text="💣", bg="#ff4444")
            self._show_result(won=False)
        elif result in ("ok", "win"):
            self._refresh_board()
            if self._game.solver_enabled():
                self._draw_overlay()
            if result == "win":
                self._on_win()

    def _on_flag(self, x, y):
        result = self._game.flag(x, y)
        if result in ("flagged", "unflagged", "win"):
            self._buttons[x][y].config(
                text="🚩" if self._game.flags[x][y] else ""
            )
            self._bombs_label.config(text=f"💣 {self._game.bombs_remaining()}")
        if result == "win":
            self._on_win()

    def _on_win(self):
        elapsed = self._game.elapsed
        m = int(elapsed // 60)
        s = int(elapsed % 60)
        ms = int((elapsed * 1000) % 1000)
        self._timer_label.config(text=f"{m:02d}:{s:02d}:{ms:03d}", fg="green")

        if self._game.cheated:
            self._show_result(won=True, cheated=True)
        elif self._game.current_preset:
            self._save_score_popup(elapsed)
        else:
            self._show_result(won=True)

    def _refresh_board(self):
        for i in range(self._game.n):
            for j in range(self._game.m):
                val = self._game.cell_value(i, j)
                if val is not None:
                    args = {"bg": "#d3d3d3", "relief": "sunken", "text": str(val)}
                    if isinstance(val, int) and val > 0:
                        args["fg"] = self.COLOR_MAP.get(val, "black")
                    elif val == " ":
                        args["text"] = ""
                    self._buttons[i][j].config(**args)

    def _toggle_overlay(self):
        enabled = self._game.toggle_solver()
        if enabled:
            self._overlay_btn.config(text="❌ Hide")
            self._draw_overlay()
        else:
            self._overlay_btn.config(text="🔍 Probabilities")
            self._clear_overlay()

    def _draw_overlay(self):
        if not self._game.playing or self._game.first_click:
            return
        probs = self._game.get_probabilities()
        for i in range(self._game.n):
            for j in range(self._game.m):
                p = probs[i][j]
                if p < 0:
                    continue
                r = int(255 * p)
                g = int(255 * (1 - p))
                self._buttons[i][j].config(
                    bg=f"#{r:02x}{g:02x}00",
                    text=f"{p * 100:.0f}%",
                    fg="white"
                )

    def _clear_overlay(self):
        for i in range(self._game.n):
            for j in range(self._game.m):
                if self._game.visible[i][j] is None and not self._game.flags[i][j]:
                    self._buttons[i][j].config(bg="lightblue", text="", fg="black")

    def _ai_step(self):
        if not self._game.playing:
            return
        self._game.mark_cheated()
        if self._game.first_click:
            self._on_click(self._game.n // 2, self._game.m // 2)
        else:
            move = self._game.ai_best_move()
            if move:
                self._on_click(move[0], move[1])
        if self._game.solver_enabled():
            self._draw_overlay()

    def _show_result(self, won, cheated=False):
        popup = tk.Toplevel(self.root)
        popup.resizable(False, False)
        popup.grab_set()

        if cheated:
            popup.title("Cheater!")
            tk.Label(popup, text="🤖  Cheater!", fg="orange",
                     font=("Arial", 22, "bold")).pack(pady=(24, 6))
            tk.Label(popup, text="Score not saved.",
                     font=("Arial", 11), fg="gray").pack(pady=(0, 16))
        elif won:
            popup.title("You won!")
            tk.Label(popup, text="🎉  WINNER!", fg="green",
                     font=("Arial", 22, "bold")).pack(pady=(24, 16))
        else:
            popup.title("Game over")
            tk.Label(popup, text="💥  LOSER!", fg="red",
                     font=("Arial", 22, "bold")).pack(pady=(24, 16))

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=(0, 16))
        tk.Button(btn_frame, text="🔁  Retry", width=12,
                  command=lambda: [popup.destroy(), self._reset()]).pack(
            side="left", padx=6)
        if won and not cheated:
            tk.Button(btn_frame, text="🏆  Leaderboard", width=14,
                      command=lambda: [popup.destroy(),
                                       self._show_leaderboard()]).pack(
                side="left", padx=6)

    def _save_score_popup(self, score):
        popup = tk.Toplevel(self.root)
        popup.title("Save Score")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="🎉  WINNER!", fg="green",
                 font=("Arial", 20, "bold")).pack(pady=(18, 4))
        tk.Label(popup,
                 text=f"{self._game.current_preset}  —  {score:.3f}s",
                 font=("Arial", 11)).pack(pady=(0, 12))

        tk.Label(popup, text="Username").pack()
        name_entry = tk.Entry(popup, width=18, justify="center")
        name_entry.pack(pady=(2, 8))
        tk.Label(popup, text="Password").pack()
        pw_entry = tk.Entry(popup, show="*", width=18, justify="center")
        pw_entry.pack(pady=(2, 12))

        def submit():
            name = name_entry.get().strip()
            password = pw_entry.get()
            if not name:
                messagebox.showerror("Error", "Username cannot be empty.")
                return
            try:
                is_pb = self._game.save_score(name, password)
                popup.destroy()
                msg = (f"🏅 New best for {self._game.current_preset}!\n"
                       f"{name}: {score:.3f}s") if is_pb else (
                    f"Not your best on {self._game.current_preset}.\n"
                    f"{name}: {score:.3f}s")
                messagebox.showinfo("Saved!" if is_pb else "Not a PB", msg)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            self._show_leaderboard()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=(0, 14))
        tk.Button(btn_frame, text="Save", width=10,
                  command=submit).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Skip", width=10,
                  command=lambda: [popup.destroy(),
                                   self._show_leaderboard()]).pack(
            side="left", padx=6)

    def _show_leaderboard(self):
        board = tk.Toplevel(self.root)
        board.title("Leaderboard")
        board.resizable(False, False)

        tk.Label(board, text="🏆  Leaderboard",
                 font=("Arial", 15, "bold")).pack(pady=(14, 6))

        frame = tk.Frame(board)
        frame.pack(padx=24, pady=6)

        for preset_name in Scoring.PRESETS:
            tk.Label(frame, text=preset_name,
                     font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
            table = tk.Frame(frame)
            table.pack(anchor="w")

            for col, (txt, w) in enumerate(
                [("#", 4), ("Name", 16), ("Best Time", 12)]
            ):
                tk.Label(table, text=txt, width=w, anchor="w",
                         font=("Arial", 10, "bold")).grid(row=0, column=col)

            entries = self._game.get_leaderboard(preset_name)
            if not entries:
                tk.Label(table, text="— no scores yet —",
                         fg="gray").grid(row=1, column=0, columnspan=3, sticky="w")
            else:
                for rank, (name, best) in enumerate(entries, start=1):
                    mm, ss = int(best // 60), int(best % 60)
                    ms = int((best * 1000) % 1000)
                    tk.Label(table, text=str(rank), width=4,
                             anchor="w").grid(row=rank, column=0)
                    tk.Label(table, text=name, width=16,
                             anchor="w").grid(row=rank, column=1)
                    tk.Label(table, text=f"{mm:02d}:{ss:02d}:{ms:03d}",
                             width=12, anchor="w").grid(row=rank, column=2)

        btn_frame = tk.Frame(board)
        btn_frame.pack(pady=(12, 14))
        tk.Button(btn_frame, text="🔁  Play Again", width=13,
                  command=lambda: [board.destroy(), self._reset()]).pack(
            side="left", padx=6)
        tk.Button(btn_frame, text="Close", width=10,
                  command=board.destroy).pack(side="left", padx=6)

    def _reset(self):
        self._game_frame.destroy()
        self._game_frame = tk.Frame(self.root)
        self._solver_bar.destroy()
        self._solver_bar = tk.Frame(self.root)
        self._timer_label.config(text="00:00:000", fg="black")
        self._bombs_label.config(text="")
        self._menu_frame.pack()

    def _on_closing(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()