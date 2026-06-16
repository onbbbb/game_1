from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class Car:
    engine: int = 30
    tires: int = 30
    aero: int = 30
    reliability: int = 50

    @property
    def performance(self) -> float:
        return (self.engine * 0.4 + self.tires * 0.3 + self.aero * 0.3) / 100


@dataclass
class RaceResult:
    position: int
    prize: int
    fastest_lap: bool
    crash: bool
    lap_times: List[float]
    laps_driven: int = 5


@dataclass
class Team:
    name: str = ""
    money: int = 500_000
    wins: int = 0
    races_total: int = 0
    car: Car = field(default_factory=Car)
    upgrade_levels: Dict[str, int] = field(default_factory=lambda: {
        "engine": 0, "tires": 0, "aero": 0, "reliability": 0
    })
    history: List[Dict] = field(default_factory=list)
    win_streak: int = 0

    def upgrade_cost(self, part: str) -> int:
        level = self.upgrade_levels.get(part, 0)
        return 50_000 + 10_000 * level

    def can_upgrade(self, part: str) -> bool:
        return self.money >= self.upgrade_cost(part)

    def apply_upgrade(self, part: str) -> bool:
        if not self.can_upgrade(part):
            return False
        cost = self.upgrade_cost(part)
        self.money -= cost
        self.upgrade_levels[part] += 1
        setattr(self.car, part, min(100, getattr(self.car, part) + 5))
        return True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "money": self.money,
            "wins": self.wins,
            "races_total": self.races_total,
            "win_streak": self.win_streak,
            "car": asdict(self.car),
            "upgrade_levels": self.upgrade_levels,
            "history": self.history[-5:],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        car = Car(**data.get("car", {}))
        return cls(
            name=data.get("name", ""),
            money=data.get("money", 500_000),
            wins=data.get("wins", 0),
            races_total=data.get("races_total", 0),
            win_streak=data.get("win_streak", 0),
            car=car,
            upgrade_levels=data.get("upgrade_levels", {
                "engine": 0, "tires": 0, "aero": 0, "reliability": 0
            }),
            history=data.get("history", []),
        )
