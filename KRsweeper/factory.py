from player import Player
from scoring import Scoring
from solver import Solver


class GameEntityFactory:
    _creators = {
        "player":  lambda: Player("Player1"),
        "scoring": lambda: Scoring(),
        "solver":  lambda: Solver(),
    }

    @staticmethod
    def create(entity_type: str):
        key = entity_type.lower()
        creator = GameEntityFactory._creators.get(key)
        if creator is None:
            raise ValueError(
                f"Unknown entity type '{entity_type}'. "
                f"Valid types: {list(GameEntityFactory._creators.keys())}"
            )
        return creator()

    @staticmethod
    def create_all():
        return (
            GameEntityFactory.create("player"),
            GameEntityFactory.create("scoring"),
            GameEntityFactory.create("solver"),
        )