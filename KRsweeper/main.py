# Main game
import random
import tkinter as tk
from player import Player

class KRsweeper:

    def __init__(self, root):
        self.root = root
        self.root.title("KRsweeper")
        self._player = None  # dar nežinome vardo

        self.n = 0
        self.m = 0
        self._grid = []
        self._visible = []
        self._flags = []
        self.buttons = []
        self._zaidziama = True

        self.start_frame = tk.Frame(root)
        self.start_frame.pack()
        self.game_frame = tk.Frame(root)

        self.status_label = tk.Label(root, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

        tk.Label(self.start_frame, text="Vardas").pack()      # ← čia
        self.entry_name = tk.Entry(self.start_frame)
        self.entry_name.pack()

        tk.Label(self.start_frame, text="Eilutės").pack()
        self.entry_rows = tk.Entry(self.start_frame)
        self.entry_rows.pack()

        tk.Label(self.start_frame, text="Stulpeliai").pack()
        self.entry_cols = tk.Entry(self.start_frame)
        self.entry_cols.pack()

        tk.Label(self.start_frame, text="Bombos").pack()
        self.entry_bombs = tk.Entry(self.start_frame)
        self.entry_bombs.pack()

        tk.Button(self.start_frame, text="Pradėti", command=self.pradeti).pack()

    def pradeti(self):
        name = self.entry_name.get()
        self._player = Player(name)
        self.n = int(self.entry_rows.get())
        self.m = int(self.entry_cols.get())
        bombu_kiekis = int(self.entry_bombs.get())

        self.start_frame.pack_forget()
        self.game_frame.pack()

        self._grid = [[0 for _ in range(self.m)] for _ in range(self.n)]
        self._visible = [[None for _ in range(self.m)] for _ in range(self.n)]
        self._flags = [[False for _ in range(self.m)] for _ in range(self.n)]

        for _ in range(bombu_kiekis):

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
                    command=lambda x=i, y=j: self.paspausta(x, y)
                )

                btn.grid(row=i, column=j)
                btn.bind("<Button-3>", lambda event, x=i, y=j: self.paflagginta(x, y))

                row.append(btn)

            self.buttons.append(row)

    def tikrint_kaimynus(self, x, y):

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

    def atidengti(self, x, y):

        if x < 0 or x >= self.n or y < 0 or y >= self.m:
            return

        if self._visible[x][y] != None:
            return

        if self._grid[x][y] == -1:
            return

        count = self.tikrint_kaimynus(x, y)

        self._visible[x][y] = " " if count == 0 else count

        if count == 0:

            for dx in range(-1, 2):
                for dy in range(-1, 2):

                    if dx == 0 and dy == 0:
                        continue

                    self.atidengti(x + dx, y + dy)

    def atnaujinti_mygtukus(self):

        for i in range(self.n):
            for j in range(self.m):

                if self._visible[i][j] != None:
                    self.buttons[i][j].config(
                        text=self._visible[i][j],
                        bg="white"
                    )

    def paspausta(self, x, y):

        if not self._zaidziama:
            return

        if self._flags[x][y]:
            return

        if self._grid[x][y] == -1:

            self.buttons[x][y].config(text="💣")
            self.status_label.config(text="Loser", fg="red")
            self._player.die()
            self._zaidziama = False
            return

        self.atidengti(x, y)
        self.atnaujinti_mygtukus()

        if self.laimejimas():
            self.status_label.config(text="WINNER", fg="green")
            self._zaidziama = False

    def paflagginta(self, x, y):

        if self._visible[x][y] != None:
            return

        self._flags[x][y] = not self._flags[x][y]

        if self._flags[x][y]:
            self.buttons[x][y].config(text="🚩")
        else:
            self.buttons[x][y].config(text="")

        if self.laimejimas():
            self.status_label.config(text="WINNER", fg="green")
            self._zaidziama = False

    def laimejimas(self):

        for i in range(self.n):
            for j in range(self.m):

                if self._grid[i][j] == -1 and not self._flags[i][j]:
                    return False

                if self._grid[i][j] != -1 and self._flags[i][j]:
                    return False

        return True


root = tk.Tk()
game = KRsweeper(root)
root.mainloop()