import unittest
from solver import Solver


class TestSolver(unittest.TestCase):

    def setUp(self):
        self.solver = Solver()
        self.n, self.m = 3, 3
        self.grid    = [[-1, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.visible = [[None, None, None], [None, 1, None], [None, None, None]]
        self.flags   = [[False] * 3 for _ in range(3)]

    def test_toggle_and_reset(self):
        self.assertFalse(self.solver.is_enabled())
        self.solver.toggle()
        self.assertTrue(self.solver.is_enabled())
        self.solver.reset()
        self.assertFalse(self.solver.is_enabled())

    def test_probabilities_valid_range(self):
        probs = self.solver.calculate_probabilities(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        self.assertEqual(probs[1][1], -1.0)
        for i in range(self.n):
            for j in range(self.m):
                if probs[i][j] >= 0:
                    self.assertGreaterEqual(probs[i][j], 0.0)
                    self.assertLessEqual(probs[i][j], 1.0)

    def test_best_move(self):
        move = self.solver.best_move(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        self.assertIsNotNone(move)
        x, y = move
        self.assertIsNone(self.visible[x][y])
        self.assertFalse(self.flags[x][y])

    def test_no_moves_returns_none(self):
        visible = [[1] * 3 for _ in range(3)]
        self.assertIsNone(self.solver.best_move(
            self.n, self.m, self.grid, visible, self.flags
        ))


if __name__ == "__main__":
    unittest.main()