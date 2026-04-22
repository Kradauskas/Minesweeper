import unittest
from player import Player


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player("TestPlayer")

    def test_initial_state(self):
        self.assertEqual(self.player.get_status(), "Alive")
        self.assertEqual(self.player.get_name(), "TestPlayer")
        self.assertEqual(self.player._flags_placed, 0)

    def test_die_and_reset(self):
        self.player.die()
        self.assertEqual(self.player.get_status(), "Dead")
        self.player.reset()
        self.assertEqual(self.player.get_status(), "Alive")

    def test_flags(self):
        self.player.place_flag()
        self.player.place_flag()
        self.assertEqual(self.player._flags_placed, 2)
        self.player.remove_flag()
        self.assertEqual(self.player._flags_placed, 1)
        self.player.reset()
        self.assertEqual(self.player._flags_placed, 0)


if __name__ == "__main__":
    unittest.main()