import unittest
from game_entity import GameEntity
from player import Player
from scoring import Scoring
from solver import Solver
from factory import GameEntityFactory


class TestFactory(unittest.TestCase):

    def test_create_all(self):
        player, scoring, solver = GameEntityFactory.create_all()
        self.assertIsInstance(player,  Player)
        self.assertIsInstance(scoring, Scoring)
        self.assertIsInstance(solver,  Solver)
        for entity in (player, scoring, solver):
            self.assertIsInstance(entity, GameEntity)

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            GameEntityFactory.create("unknown")


if __name__ == "__main__":
    unittest.main()