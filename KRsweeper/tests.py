import unittest
import os
import json
import tempfile

from game_entity import GameEntity
from player import Player
from scoring import Scoring
from solver import Solver
from factory import GameEntityFactory


# ---------------------------------------------------------------------------
# Player tests
# ---------------------------------------------------------------------------

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player("TestPlayer")

    def test_initial_status_is_alive(self):
        self.assertEqual(self.player.get_status(), "Alive")

    def test_die_changes_status(self):
        self.player.die()
        self.assertEqual(self.player.get_status(), "Dead")

    def test_reset_revives_player(self):
        self.player.die()
        self.player.reset()
        self.assertEqual(self.player.get_status(), "Alive")

    def test_flag_count(self):
        self.player.place_flag()
        self.player.place_flag()
        self.assertEqual(self.player._flags_placed, 2)
        self.player.remove_flag()
        self.assertEqual(self.player._flags_placed, 1)

    def test_reset_clears_flags(self):
        self.player.place_flag()
        self.player.reset()
        self.assertEqual(self.player._flags_placed, 0)

    def test_get_name(self):
        self.assertEqual(self.player.get_name(), "TestPlayer")


# ---------------------------------------------------------------------------
# Scoring tests
# ---------------------------------------------------------------------------

class TestScoring(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        )
        self.tmp.write("{}")
        self.tmp.close()
        self.scoring = Scoring(scores_file=self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_save_new_score(self):
        result = self.scoring.save_score("Easy", "alice", "pw1", 10.0)
        self.assertTrue(result)

    def test_better_score_replaces(self):
        self.scoring.save_score("Easy", "alice", "pw1", 10.0)
        result = self.scoring.save_score("Easy", "alice", "pw1", 8.0)
        self.assertTrue(result)
        lb = self.scoring.get_leaderboard("Easy")
        self.assertAlmostEqual(lb[0][1], 8.0)

    def test_worse_score_not_saved(self):
        self.scoring.save_score("Easy", "alice", "pw1", 10.0)
        result = self.scoring.save_score("Easy", "alice", "pw1", 15.0)
        self.assertFalse(result)

    def test_wrong_password_raises(self):
        self.scoring.save_score("Easy", "alice", "pw1", 10.0)
        with self.assertRaises(ValueError):
            self.scoring.save_score("Easy", "alice", "wrongpw", 5.0)

    def test_leaderboard_sorted(self):
        self.scoring.save_score("Easy", "alice", "pw1", 20.0)
        self.scoring.save_score("Easy", "bob",   "pw2", 10.0)
        self.scoring.save_score("Easy", "carol", "pw3", 15.0)
        lb = self.scoring.get_leaderboard("Easy")
        times = [t for _, t in lb]
        self.assertEqual(times, sorted(times))

    def test_separate_presets(self):
        self.scoring.save_score("Easy",   "alice", "pw1", 10.0)
        self.scoring.save_score("Medium", "alice", "pw1", 20.0)
        easy_lb   = self.scoring.get_leaderboard("Easy")
        medium_lb = self.scoring.get_leaderboard("Medium")
        self.assertEqual(len(easy_lb), 1)
        self.assertEqual(len(medium_lb), 1)
        self.assertAlmostEqual(easy_lb[0][1],   10.0)
        self.assertAlmostEqual(medium_lb[0][1], 20.0)

    def test_get_status_reflects_count(self):
        self.scoring.save_score("Easy", "alice", "pw1", 10.0)
        # 1 score across all presets
        self.assertIn("1", self.scoring.get_status())

    def test_reset_clears_session(self):
        self.scoring.save_score("Easy", "alice", "pw1", 10.0)
        self.scoring.reset()
        self.assertEqual(self.scoring.get_session_scores(), [])

    def test_empty_file_handled(self):
        # Write empty file — should not crash
        with open(self.tmp.name, "w") as f:
            f.write("")
        result = self.scoring.save_score("Easy", "alice", "pw1", 5.0)
        self.assertTrue(result)


class TestSolver(unittest.TestCase):

    def setUp(self):
        self.solver = Solver()
        # 3x3 grid, mine at (0,0)
        #  -1  0  0
        #   0  0  0
        #   0  0  0
        self.n, self.m = 3, 3
        self.grid = [
            [-1, 0, 0],
            [0,  0, 0],
            [0,  0, 0],
        ]
        # Reveal (1,1) with value 1 (one mine neighbour)
        self.visible = [
            [None, None, None],
            [None, 1,    None],
            [None, None, None],
        ]
        self.flags = [[False] * 3 for _ in range(3)]

    def test_toggle(self):
        self.assertFalse(self.solver.is_enabled())
        self.solver.toggle()
        self.assertTrue(self.solver.is_enabled())
        self.solver.toggle()
        self.assertFalse(self.solver.is_enabled())

    def test_reset_disables(self):
        self.solver.toggle()
        self.solver.reset()
        self.assertFalse(self.solver.is_enabled())

    def test_get_status(self):
        self.assertEqual(self.solver.get_status(), "Solver OFF")
        self.solver.toggle()
        self.assertEqual(self.solver.get_status(), "Solver ON")

    def test_probabilities_revealed_cells_are_negative(self):
        probs = self.solver.calculate_probabilities(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        self.assertEqual(probs[1][1], -1.0)  # (1,1) is revealed

    def test_probabilities_flagged_cells_are_negative(self):
        self.flags[0][1] = True
        probs = self.solver.calculate_probabilities(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        self.assertEqual(probs[0][1], -1.0)

    def test_probabilities_in_range(self):
        probs = self.solver.calculate_probabilities(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        for i in range(self.n):
            for j in range(self.m):
                if probs[i][j] >= 0:
                    self.assertGreaterEqual(probs[i][j], 0.0)
                    self.assertLessEqual(probs[i][j], 1.0)

    def test_best_move_returns_valid_cell(self):
        move = self.solver.best_move(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        self.assertIsNotNone(move)
        x, y = move
        self.assertIsNone(self.visible[x][y])
        self.assertFalse(self.flags[x][y])

    def test_best_move_is_lowest_probability(self):
        probs = self.solver.calculate_probabilities(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        move = self.solver.best_move(
            self.n, self.m, self.grid, self.visible, self.flags
        )
        self.assertIsNotNone(move)
        x, y = move
        min_prob = min(
            probs[i][j]
            for i in range(self.n) for j in range(self.m)
            if probs[i][j] >= 0
        )
        self.assertAlmostEqual(probs[x][y], min_prob)

    def test_no_moves_returns_none(self):
        # Mark everything as flagged or revealed
        visible = [[1] * 3 for _ in range(3)]
        move = self.solver.best_move(
            self.n, self.m, self.grid, visible, self.flags
        )
        self.assertIsNone(move)

class TestFactory(unittest.TestCase):

    def test_create_player(self):
        entity = GameEntityFactory.create("player")
        self.assertIsInstance(entity, Player)

    def test_create_scoring(self):
        entity = GameEntityFactory.create("scoring")
        self.assertIsInstance(entity, Scoring)

    def test_create_solver(self):
        entity = GameEntityFactory.create("solver")
        self.assertIsInstance(entity, Solver)

    def test_create_unknown_raises(self):
        with self.assertRaises(ValueError):
            GameEntityFactory.create("unknown")

    def test_create_all_returns_tuple(self):
        player, scoring, solver = GameEntityFactory.create_all()
        self.assertIsInstance(player,  Player)
        self.assertIsInstance(scoring, Scoring)
        self.assertIsInstance(solver,  Solver)

    def test_all_entities_are_game_entities(self):
        player, scoring, solver = GameEntityFactory.create_all()
        for entity in (player, scoring, solver):
            self.assertIsInstance(entity, GameEntity)


if __name__ == "__main__":
    unittest.main()