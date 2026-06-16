import json
import os
from typing import Optional
from game_state import Team

SAVE_FILE = "pitstop_save.json"


def save_game(team: Team):
    data = team.to_dict()
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_game() -> Optional[Team]:
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Team.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


def reset_game():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
