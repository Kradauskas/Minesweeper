from game_entity import GameEntity

class Player(GameEntity):
    def __init__(self, name):
        super().__init__(name)
        self._alive = True
        self._flags_placed = 0

    def place_flag(self):
        self._flags_placed += 1
    
    def remove_flag(self):
        self._flags_placed -= 1
    
    def die(self):
        self._alive = False
        return False

    def get_status(self):
        return "Alive" if self._alive else "Dead"

    def reset(self):
        self._alive = True
        self._flags_placed = 0
        
    def get_name(self):
        return self._name
