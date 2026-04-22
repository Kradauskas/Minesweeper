import unittest
import os
import tempfile
from scoring import Scoring


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

    def test_save_and_improve_score(self):
        self.assertTrue(self.scoring.save_score("Easy", "alice", "pw", 10.0))
        self.assertTrue(self.scoring.save_score("Easy", "alice", "pw", 8.0))
        self.assertAlmostEqual(self.scoring.get_leaderboard("Easy")[0][1], 8.0)

    def test_worse_score_not_saved(self):
        self.scoring.save_score("Easy", "alice", "pw", 10.0)
        self.assertFalse(self.scoring.save_score("Easy", "alice", "pw", 15.0))

    def test_wrong_password_raises(self):
        self.scoring.save_score("Easy", "alice", "pw", 10.0)
        with self.assertRaises(ValueError):
            self.scoring.save_score("Easy", "alice", "wrongpw", 5.0)

    def test_leaderboard_sorted(self):
        self.scoring.save_score("Easy", "alice", "pw1", 20.0)
        self.scoring.save_score("Easy", "bob",   "pw2", 10.0)
        times = [t for _, t in self.scoring.get_leaderboard("Easy")]
        self.assertEqual(times, sorted(times))

    def test_reset_clears_session(self):
        self.scoring.save_score("Easy", "alice", "pw", 10.0)
        self.scoring.reset()
        self.assertEqual(self.scoring.get_session_scores(), [])


if __name__ == "__main__":
    unittest.main()