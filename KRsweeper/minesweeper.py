import random
import time
from factory import GameEntityFactory


class Minesweeper:

    def __init__(self):
        self._player, self._scoring, self._solver = GameEntityFactory.create_all()

        self._entities = [self._player, self._scoring, self._solver]

        self.n = 0
        self.m = 0
        self._mine_amount = 0
        self._grid = []
        self._visible = []
        self._flags = []

        self._playing = False
        self._first_click = True
        self._cheated = False
        self._current_preset = None
        self.start_time = None
        self.elapsed = 0.0

    def new_game(self, rows, cols, mines, preset=None):
        for entity in self._entities:
            entity.reset()

        self.n = rows
        self.m = cols
        self._mine_amount = mines
        self._current_preset = preset

        self._grid = [[0] * cols for _ in range(rows)]
        self._visible = [[None] * cols for _ in range(rows)]
        self._flags = [[False] * cols for _ in range(rows)]

        self._playing = True
        self._first_click = True
        self._cheated = False
        self.start_time = None
        self.elapsed = 0.0

        self._place_mines(skip_x=None, skip_y=None)

    def _place_mines(self, skip_x, skip_y):
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
            if self._grid[x][y] == -1 or (x, y) in safe:
                continue
            self._grid[x][y] = -1
            placed += 1

    def click(self, x, y):
        if not self._playing:
            return "already_done"
        if self._flags[x][y]:
            return "flagged"

        was_first = self._first_click
        if self._first_click:
            self._first_click = False
            self._place_mines(skip_x=x, skip_y=y)
            self.start_time = time.time()

        if self._grid[x][y] == -1:
            self._playing = False
            self._player.die()
            self.elapsed = 0.0
            return "explode"

        self._open(x, y)

        if not was_first and self._check_win():
            self._playing = False
            self.elapsed = time.time() - self.start_time
            return "win"

        return "ok"

    def flag(self, x, y):
        if not self._playing:
            return "already_done"
        if self._visible[x][y] is not None:
            return "revealed"

        self._flags[x][y] = not self._flags[x][y]
        result = "flagged" if self._flags[x][y] else "unflagged"

        if self._check_win():
            self._playing = False
            self.elapsed = time.time() - self.start_time
            return "win"

        return result

    def mark_cheated(self):
        self._cheated = True

    def _neighbours(self, x, y):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.n and 0 <= ny < self.m:
                    yield nx, ny

    def count_mine_neighbours(self, x, y):
        return sum(1 for nx, ny in self._neighbours(x, y)
                   if self._grid[nx][ny] == -1)

    def _open(self, x, y):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if not (0 <= cx < self.n and 0 <= cy < self.m):
                continue
            if self._visible[cx][cy] is not None:
                continue
            if self._grid[cx][cy] == -1:
                continue
            count = self.count_mine_neighbours(cx, cy)
            self._visible[cx][cy] = " " if count == 0 else count
            if count == 0:
                for nx, ny in self._neighbours(cx, cy):
                    stack.append((nx, ny))

    def _check_win(self):
        classic = all(
            (self._grid[i][j] == -1) == self._flags[i][j]
            for i in range(self.n) for j in range(self.m)
        )
        if classic:
            return True
        if self._cheated:
            return all(
                self._grid[i][j] == -1 or self._visible[i][j] is not None
                for i in range(self.n) for j in range(self.m)
            )
        return False

    def toggle_solver(self):
        self._cheated = True
        return self._solver.toggle()

    def solver_enabled(self):
        return self._solver.is_enabled()

    def get_probabilities(self):
        return self._solver.calculate_probabilities(
            self.n, self.m, self._grid, self._visible, self._flags
        )

    def ai_best_move(self):
        return self._solver.best_move(
            self.n, self.m, self._grid, self._visible, self._flags
        )

    def save_score(self, name, password):
        return self._scoring.save_score(
            self._current_preset, name, password, self.elapsed
        )

    def get_leaderboard(self, preset):
        return self._scoring.get_leaderboard(preset)

    @property
    def playing(self):
        return self._playing

    @property
    def first_click(self):
        return self._first_click

    @property
    def cheated(self):
        return self._cheated

    @property
    def current_preset(self):
        return self._current_preset

    @property
    def flags(self):
        return self._flags

    @property
    def visible(self):
        return self._visible

    @property
    def grid(self):
        return self._grid

    def bombs_remaining(self):
        flags_placed = sum(
            self._flags[i][j]
            for i in range(self.n) for j in range(self.m)
        )
        return self._mine_amount - flags_placed

    def cell_value(self, x, y):
        return self._visible[x][y]