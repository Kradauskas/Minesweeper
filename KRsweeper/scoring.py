import json
import os
from game_entity import GameEntity


class Scoring(GameEntity): 

    PRESETS = {
        "Easy":   {"rows": 5,  "cols": 5,  "mines": 5},
        "Medium": {"rows": 10, "cols": 10, "mines": 15},
        "Hard":   {"rows": 16, "cols": 16, "mines": 40},
    }

    def __init__(self, scores_file="scores.json"):
        super().__init__("Scoring")        
        self._scores_file = scores_file     
        self._session_scores = []            

    def get_status(self):
        total = sum(len(self.get_leaderboard(p)) for p in self.PRESETS)
        return f"{total} score(s) on leaderboards"

    def reset(self):
        self._session_scores = []
        self._status = "active"

    def _load(self):
        if os.path.exists(self._scores_file):
            with open(self._scores_file, "r") as f:
                return json.load(f)
        return {}

    def _save(self, data):
        with open(self._scores_file, "w") as f:
            json.dump(data, f, indent=4)

    def save_score(self, preset, name, password, score):
        data = self._load()

        if preset not in data:
            data[preset] = {}

        preset_data = data[preset]

        if name in preset_data:
            if preset_data[name]["password"] != password:
                raise ValueError("Incorrect password!")
            if score >= preset_data[name]["best_score"]:
                self._session_scores.append((preset, name, score))
                return False
            preset_data[name]["best_score"] = score
        else:
            preset_data[name] = {"password": password, "best_score": score}

        self._session_scores.append((preset, name, score))
        self._save(data)
        return True

    def get_leaderboard(self, preset):
        data = self._load()
        preset_data = data.get(preset, {})
        entries = [(name, info["best_score"]) for name, info in preset_data.items()]
        entries.sort(key=lambda x: x[1])
        return entries

    def get_session_scores(self):
        return list(self._session_scores)