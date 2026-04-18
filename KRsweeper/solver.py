from game_entity import GameEntity


class Solver(GameEntity):

    def __init__(self):
        super().__init__("Solver")  
        self._enabled = False       

    def get_status(self):
        return "Solver ON" if self._enabled else "Solver OFF"

    def reset(self):
        self._enabled = False
        self._status = "active"

    def toggle(self):
        self._enabled = not self._enabled
        return self._enabled

    def is_enabled(self):
        return self._enabled

    def calculate_probabilities(self, n, m, grid, visible, flags):

        probs = [[-1.0] * m for _ in range(n)]

        def neighbours(x, y):
            result = []
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < m:
                        result.append((nx, ny))
            return result

        def hidden_unflagged(x, y):
            return [(nx, ny) for nx, ny in neighbours(x, y)
                    if visible[nx][ny] is None and not flags[nx][ny]]

        def flagged_neighbours(x, y):
            return sum(1 for nx, ny in neighbours(x, y) if flags[nx][ny])

        total_hidden = sum(
            1 for i in range(n) for j in range(m)
            if visible[i][j] is None and not flags[i][j]
        )
        total_flags = sum(1 for i in range(n) for j in range(m) if flags[i][j])
        total_mines = sum(1 for i in range(n) for j in range(m) if grid[i][j] == -1)
        remaining_mines = total_mines - total_flags
        global_prob = (remaining_mines / total_hidden) if total_hidden > 0 else 0.0

        for i in range(n):
            for j in range(m):
                if visible[i][j] is not None or flags[i][j]:
                    continue 
                contributions = []
                for nx, ny in neighbours(i, j):
                    val = visible[nx][ny]
                    if not isinstance(val, int) or val <= 0:
                        continue
                    hf = hidden_unflagged(nx, ny)
                    if not hf:
                        continue
                    mines_left = val - flagged_neighbours(nx, ny)
                    if mines_left < 0:
                        mines_left = 0
                    contributions.append(mines_left / len(hf))

                if contributions:
                    probs[i][j] = sum(contributions) / len(contributions)
                else:
                    probs[i][j] = global_prob

        return probs

    def best_move(self, n, m, grid, visible, flags):
        probs = self.calculate_probabilities(n, m, grid, visible, flags)
        best = None
        best_prob = float("inf")
        for i in range(n):
            for j in range(m):
                if probs[i][j] >= 0 and probs[i][j] < best_prob:
                    best_prob = probs[i][j]
                    best = (i, j)
        return best