import random
import tkinter as tk


class Minesweeper:

    def __init__(self, root):

        self.root = root
        self.root.title("KRsweeper")

        self.n = 0
        self.m = 0
        self.grid = []
        self.visible = []
        self.flags = []
        self.buttons = []
        self.zaidziama = True

        self.start_frame = tk.Frame(root)
        self.start_frame.pack()

        self.game_frame = tk.Frame(root)

        self.status_label = tk.Label(root, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

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

        self.n = int(self.entry_rows.get())
        self.m = int(self.entry_cols.get())
        bombu_kiekis = int(self.entry_bombs.get())

        self.start_frame.pack_forget()
        self.game_frame.pack()

        self.grid = [[0 for _ in range(self.m)] for _ in range(self.n)]
        self.visible = [[None for _ in range(self.m)] for _ in range(self.n)]
        self.flags = [[False for _ in range(self.m)] for _ in range(self.n)]

        for _ in range(bombu_kiekis):

            x = random.randint(0, self.n - 1)
            y = random.randint(0, self.m - 1)

            while self.grid[x][y] == -1:
                x = random.randint(0, self.n - 1)
                y = random.randint(0, self.m - 1)

            self.grid[x][y] = -1

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
                    if self.grid[nx][ny] == -1:
                        count += 1

        return count

    def atidengti(self, x, y):

        if x < 0 or x >= self.n or y < 0 or y >= self.m:
            return

        if self.visible[x][y] != None:
            return

        if self.grid[x][y] == -1:
            return

        count = self.tikrint_kaimynus(x, y)

        self.visible[x][y] = " " if count == 0 else count

        if count == 0:

            for dx in range(-1, 2):
                for dy in range(-1, 2):

                    if dx == 0 and dy == 0:
                        continue

                    self.atidengti(x + dx, y + dy)

    def atnaujinti_mygtukus(self):

        for i in range(self.n):
            for j in range(self.m):

                if self.visible[i][j] != None:
                    self.buttons[i][j].config(
                        text=self.visible[i][j],
                        bg="white"
                    )

    def paspausta(self, x, y):

        if not self.zaidziama:
            return

        if self.flags[x][y]:
            return

        if self.grid[x][y] == -1:

            self.buttons[x][y].config(text="💣")
            self.status_label.config(text="Loser", fg="red")
            self.zaidziama = False
            return

        self.atidengti(x, y)
        self.atnaujinti_mygtukus()

        if self.laimejimas():
            self.status_label.config(text="WINNER", fg="green")
            self.zaidziama = False

    def paflagginta(self, x, y):

        if self.visible[x][y] != None:
            return

        self.flags[x][y] = not self.flags[x][y]

        if self.flags[x][y]:
            self.buttons[x][y].config(text="🚩")
        else:
            self.buttons[x][y].config(text="")

        if self.laimejimas():
            self.status_label.config(text="WINNER", fg="green")
            self.zaidziama = False

    def laimejimas(self):

        for i in range(self.n):
            for j in range(self.m):

                if self.grid[i][j] == -1 and not self.flags[i][j]:
                    return False

                if self.grid[i][j] != -1 and self.flags[i][j]:
                    return False

        return True


root = tk.Tk()
game = Minesweeper(root)
root.mainloop()