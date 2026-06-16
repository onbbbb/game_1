import random
from typing import List, Tuple, Optional
from game_state import Car, RaceResult


STRATEGIES = {
    "economy": {"name": "Экономная", "speed": 0.9, "tire_wear": 0.5, "reliability_factor": 0.5},
    "normal": {"name": "Нормальная", "speed": 1.0, "tire_wear": 1.0, "reliability_factor": 1.0},
    "aggressive": {"name": "Агрессивная", "speed": 1.2, "tire_wear": 1.5, "reliability_factor": 1.5},
}

EVENTS = [
    ("Обогнал соперника", 0.0),
    ("Вылет на обочину (-2 сек)", 2.0),
    ("Лучший круг!", -1.5),
    ("Проблемы с тормозами", 1.0),
    ("Пит-стоп (+3 сек)", 3.0),
]


def generate_opponents(count: int = 9) -> List[float]:
    return [random.uniform(0.4, 0.8) for _ in range(count)]


def simulate_lap(car: Car, strategy: dict, lap: int) -> Tuple[float, Optional[str], bool, float, bool]:
    base_time = random.uniform(58, 62)
    perf_bonus = car.performance * 10
    strategy_factor = strategy["speed"]

    lap_time = base_time - perf_bonus * strategy_factor

    tire_wear = strategy["tire_wear"] * random.uniform(0.8, 1.2)
    car.tires = max(0, car.tires - tire_wear)

    reliability_check = car.reliability / 100 * strategy["reliability_factor"]
    if random.random() > reliability_check:
        return lap_time, None, lap, 0.0, True

    event_text = None
    event_penalty = 0.0
    if random.random() < 0.3:
        event_text, penalty = random.choice(EVENTS)
        event_penalty = penalty
        if event_text == "Лучший круг!":
            event_penalty = -1.5

    lap_time += event_penalty

    return lap_time, event_text, lap, tire_wear, False


def run_race(car: Car, strategy: dict) -> RaceResult:
    car = Car(car.engine, car.tires, car.aero, car.reliability)

    lap_times = []
    events = []
    crash = False
    laps_driven = 0

    for lap in range(1, 6):
        lap_time, event_text, _, tire_wear, crashed = simulate_lap(car, strategy, lap)
        laps_driven = lap

        if crashed:
            lap_times.append(round(lap_time, 1))
            events.append((lap, f"Поломка на {lap}-м круге!", tire_wear))
            crash = True
            break

        lap_times.append(round(lap_time, 1))
        if event_text:
            events.append((lap, event_text, tire_wear))
        else:
            events.append((lap, None, tire_wear))

    total_time = sum(lap_times)
    opponent_times = []
    for perf in generate_opponents():
        opp_time = sum(random.uniform(58, 62) - perf * 10 * strategy["speed"] for _ in range(laps_driven))
        opponent_times.append(opp_time)

    all_times = [(total_time, 0)] + [(t, i + 1) for i, t in enumerate(opponent_times)]
    all_times.sort(key=lambda x: x[0])

    position = next(i for i, (t, _) in enumerate(all_times) if t == total_time and _ == 0) + 1

    fastest_lap = min(lap_times) < min([random.uniform(58, 62) for _ in range(9)])

    prize_table = {
        1: (200_000, 50_000),
        2: (150_000, 30_000),
        3: (120_000, 20_000),
        4: (80_000, 0),
        5: (80_000, 0),
        6: (50_000, 0),
        7: (50_000, 0),
        8: (50_000, 0),
        9: (30_000, 0),
        10: (30_000, 0),
    }

    prize, bonus = prize_table.get(position, (10_000, 0))
    if crash:
        prize = 10_000
        bonus = 0

    return RaceResult(
        position=position,
        prize=prize,
        fastest_lap=fastest_lap,
        crash=crash,
        lap_times=lap_times,
        laps_driven=laps_driven,
    ), events
