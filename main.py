import flet as ft
from game_state import Team, Car
from race_logic import run_race, STRATEGIES
from data_manager import save_game, load_game, reset_game


def main(page: ft.Page):
    page.title = "Гоночный симулятор"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.width = 520
    page.window.height = 800
    page.window.resizable = False

    team = load_game()
    saved_name = team.name if team else ""

    strategy_name = "normal"
    race_events = []
    race_result = None
    current_lap = 0
    race_lap_times = []

    name_field = ft.Ref[ft.TextField]()

    def show_start():
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("🏁 Гоночный симулятор", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Гоночный менеджер", size=16, color=ft.Colors.GREY_400),
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    ft.TextField(
                        label="Название команды",
                        value=saved_name,
                        width=300,
                        on_submit=lambda e: start_game(e.control.value.strip()),
                        ref=name_field,
                    ),
                    ft.FilledButton(
                        "СТАРТ",
                        width=300,
                        on_click=lambda e: start_game(
                            name_field.current.value.strip()
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )

    def start_game(name: str):
        nonlocal team
        if not name:
            name = "Команда"
        team = Team(name=name)
        save_game(team)
        show_garage()

    def show_garage():
        nonlocal race_result, race_events, current_lap, race_lap_times
        race_result = None
        race_events = []
        current_lap = 0
        race_lap_times = []

        page.clean()

        stats = ft.Column(
            [
                ft.Text(f"💳 БАЛАНС: {team.money:,} ₽".replace(",", " "), size=18, weight=ft.FontWeight.BOLD),
                ft.Text(f"🥇 ПОБЕД: {team.wins} / ЗАЕЗДОВ: {team.races_total}", size=14),
                ft.Text(f"⚡ СТРИК: {team.win_streak}", size=14, color=ft.Colors.ORANGE_400 if team.win_streak >= 2 else ft.Colors.GREY_400),
            ],
            spacing=4,
        )

        bar_width = 200
        car_stats = ft.Column(
            [
                ft.Row([
                    ft.Text("⚙ Двигатель:", width=150),
                    ft.ProgressBar(width=bar_width, value=team.car.engine / 100, color=ft.Colors.BLUE_400),
                    ft.Text(f"{team.car.engine}", width=30),
                ], spacing=5),
                ft.Row([
                    ft.Text("⚪ Шины:", width=150),
                    ft.ProgressBar(width=bar_width, value=team.car.tires / 100, color=ft.Colors.GREEN_400),
                    ft.Text(f"{team.car.tires}", width=30),
                ], spacing=5),
                ft.Row([
                    ft.Text("💨 Аэродинамика:", width=150),
                    ft.ProgressBar(width=bar_width, value=team.car.aero / 100, color=ft.Colors.PURPLE_400),
                    ft.Text(f"{team.car.aero}", width=30),
                ], spacing=5),
                ft.Row([
                    ft.Text("🛡 Надёжность:", width=150),
                    ft.ProgressBar(width=bar_width, value=team.car.reliability / 100, color=ft.Colors.ORANGE_400),
                    ft.Text(f"{team.car.reliability}", width=30),
                ], spacing=5),
            ],
            spacing=8,
        )

        parts = ["engine", "tires", "aero", "reliability"]
        part_names = {
            "engine": "⚙ двигатель",
            "tires": "⚪ шины",
            "aero": "💨 аэродинамику",
            "reliability": "🛡 надёжность",
        }
        upgrade_buttons = []
        for part in parts:
            cost = team.upgrade_cost(part)
            can = team.can_upgrade(part)
            lvl = team.upgrade_levels[part]
            btn = ft.FilledButton(
                f"Улучшить {part_names[part]} ({cost:,} ₽)".replace(",", " "),
                disabled=not can,
                width=300,
                on_click=lambda e, p=part: do_upgrade(p),
            )
            upgrade_buttons.append(btn)

        start_btn = ft.FilledTonalButton(
            "🚥 СТАРТ ГОНКИ",
            width=300,
            on_click=lambda e: show_strategy_select(),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_700,
            ),
        )

        reset_btn = ft.TextButton(
            "Сбросить прогресс",
            on_click=lambda e: confirm_reset(),
        )

        history_items = []
        for h in reversed(team.history[-5:]):
            pos = h["position"]
            pos_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}
            emoji = pos_emoji.get(pos, f"#{pos}")
            pos_name = h.get("position_name", f"{pos}-е место")
            prize_str = f"{h['prize']:,} ₽".replace(",", " ")
            history_items.append(
                ft.Text(f"• Гонка #{h['race']}: {emoji} {pos_name} ({prize_str})")
            )

        history_col = ft.Column(history_items, spacing=2) if history_items else ft.Text("Пока нет гонок", italic=True, color=ft.Colors.GREY_500)

        page.add(
            ft.Column(
                [
                    ft.Text("🏁 Гоночный симулятор", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Команда: {team.name}", size=14, color=ft.Colors.GREY_400),
                    ft.Divider(height=10),
                    stats,
                    ft.Divider(height=10),
                    ft.Text("ХАРАКТЕРИСТИКИ", size=14, weight=ft.FontWeight.BOLD),
                    car_stats,
                    ft.Divider(height=10),
                    ft.Column(upgrade_buttons, spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Divider(height=10),
                    start_btn,
                    ft.Divider(height=10),
                    ft.Text("📋 ИСТОРИЯ:", size=14, weight=ft.FontWeight.BOLD),
                    history_col,
                    ft.Divider(height=10),
                    reset_btn,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                spacing=5,
            )
        )

    def do_upgrade(part: str):
        if team.apply_upgrade(part):
            save_game(team)
        show_garage()

    def show_strategy_select():
        page.clean()

        strategy_btns = []
        for key, s in STRATEGIES.items():
            btn = ft.FilledButton(
                s["name"],
                width=300,
                on_click=lambda e, k=key: start_race(k),
            )
            strategy_btns.append(btn)

        page.add(
            ft.Column(
                [
                    ft.Text("🚥 ВЫБОР СТРАТЕГИИ", size=22, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    ft.Text("Выберите стратегию на гонку:", size=14),
                    ft.Divider(height=10),
                    *strategy_btns,
                    ft.Divider(height=20),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Стратегия  | Скорость | Износ шин | Риск", weight=ft.FontWeight.BOLD),
                                ft.Text("🟩 Экономная  | ×0.9     | ×0.5      | ×0.5"),
                                ft.Text("🟨 Нормальная | ×1.0     | ×1.0      | ×1.0"),
                                ft.Text("🟥 Агрессивная| ×1.2     | ×1.5      | ×1.5"),
                            ],
                            spacing=2,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=10,
                    ),
                    ft.Divider(height=20),
                    ft.TextButton("Назад", on_click=lambda e: show_garage()),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            )
        )

    def start_race(strat_key: str):
        nonlocal strategy_name, race_result, race_events, current_lap, race_lap_times

        strategy_name = strat_key
        race_result, race_events = run_race(team.car, STRATEGIES[strategy_name])
        race_lap_times = race_result.lap_times
        current_lap = 0

        show_race_lap()

    def show_race_lap():
        nonlocal current_lap

        if current_lap >= len(race_lap_times):
            show_race_result()
            return

        page.clean()

        lap_num = current_lap + 1
        total_laps = race_result.laps_driven
        lap_time = race_lap_times[current_lap]
        _, event_text, _ = race_events[current_lap] if current_lap < len(race_events) else (None, None, None)

        strat = STRATEGIES[strategy_name]
        strat_color = {"economy": ft.Colors.GREEN_400, "normal": ft.Colors.YELLOW_400, "aggressive": ft.Colors.RED_400}
        strat_emoji = {"economy": "🟩", "normal": "🟨", "aggressive": "🟥"}

        broadcast_items = []
        for i in range(current_lap + 1):
            t = race_lap_times[i]
            ev = race_events[i][1] if i < len(race_events) else None
            line = f"{strat_emoji[strategy_name]} Круг {i+1}: {t:.1f} сек"
            if ev:
                line += f" — {ev}"
            broadcast_items.append(ft.Text(line))

        tire_pct = max(0, int(team.car.tires))

        fastest = min(race_lap_times[:current_lap + 1])

        continue_btn = ft.FilledButton(
            "⏭ ПРОДОЛЖИТЬ СЛЕДУЮЩИЙ КРУГ",
            width=300,
            on_click=lambda e: advance_lap(),
        )

        if race_result.crash and lap_num == race_result.laps_driven:
            continue_btn = ft.FilledButton(
                "🚥 К ГОНКЕ",
                width=300,
                on_click=lambda e: show_race_result(),
            )

        strat_name = STRATEGIES[strategy_name]["name"]

        page.add(
            ft.Column(
                [
                    ft.Text(f"🚥 ГОНКА: ВЕЛИКИЙ ПРИЗ", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"КРУГ {lap_num}/{total_laps} | Стратегия: {strat_name}", size=14, color=ft.Colors.GREY_400),
                    ft.Divider(height=10),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("📣 ТРАНСЛЯЦИЯ:", weight=ft.FontWeight.BOLD),
                                *broadcast_items,
                            ],
                            spacing=3,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=10,
                        width=350,
                    ),
                    ft.Divider(height=10),
                    ft.Row([
                        ft.Column([
                            ft.Text(f"📈 ПОЗИЦИЯ: {race_result.position}-е место", size=14),
                            ft.Text(f"⏰ ЛУЧШИЙ КРУГ: {fastest:.1f} сек", size=14),
                            ft.Text(f"⚪ СОСТОЯНИЕ ШИН: {tire_pct}%", size=14),
                        ], spacing=4),
                    ]),
                    ft.Divider(height=10),
                    continue_btn,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            )
        )

    def advance_lap():
        nonlocal current_lap
        current_lap += 1
        show_race_lap()

    def show_race_result():
        page.clean()

        pos = race_result.position
        if pos == 1:
            pos_text = f"🥇 1 МЕСТО! ПОБЕДА! 🥇"
        elif pos == 2:
            pos_text = f"🥈 2 МЕСТО!"
        elif pos == 3:
            pos_text = f"🥉 3 МЕСТО!"
        else:
            pos_text = f"#{pos} МЕСТО"

        prize_lines = [f"💳 ПРИЗОВЫЕ: {race_result.prize:,} ₽".replace(",", " ")]
        total_prize = race_result.prize
        if race_result.fastest_lap:
            prize_lines.append(f"✨ Бонус (лучший круг): +20 000 ₽")
            total_prize += 20_000
        if not race_result.crash and pos == 1 and team.win_streak >= 2:
            prize_lines.append(f"⚡ Стрик 3+ побед: +100 000 ₽")
            total_prize += 100_000

        stats_lines = [
            f"• Финиш: {pos}-е место",
            f"• Лучший круг: {min(race_result.lap_times):.1f} сек" if race_result.lap_times else "",
            f"• Кругов пройдено: {race_result.laps_driven}/5",
        ]
        if race_result.crash:
            stats_lines.append("💢 СХОД С ДИСТАНЦИИ")

        def finish_race():
            nonlocal team
            team.money += total_prize
            team.races_total += 1
            if pos == 1:
                team.wins += 1
                team.win_streak += 1
            else:
                team.win_streak = 0
            team.history.append({
                "race": team.races_total,
                "position": pos,
                "prize": total_prize,
            })
            save_game(team)
            show_garage()

        page.add(
            ft.Column(
                [
                    ft.Text("👑 РЕЗУЛЬТАТ 👑", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    ft.Text(pos_text, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW_400 if pos == 1 else ft.Colors.WHITE),
                    ft.Divider(height=15),
                    *[ft.Text(l, size=14) for l in prize_lines],
                    ft.Divider(height=15),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("📈 СТАТИСТИКА:", weight=ft.FontWeight.BOLD),
                                *[ft.Text(l, size=13) for l in stats_lines if l],
                            ],
                            spacing=3,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=10,
                    ),
                    ft.Divider(height=20),
                    ft.FilledButton(
                        "ВЕРНУТЬСЯ В ГАРАЖ",
                        width=300,
                        on_click=lambda e: finish_race(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            )
        )

    def confirm_reset():
        dlg = ft.AlertDialog(
            title=ft.Text("Сброс прогресса"),
            content=ft.Text("Вы уверены? Весь прогресс будет потерян!"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: close_dlg(dlg)),
                ft.FilledButton("Сбросить", on_click=lambda e: do_reset(dlg)),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def close_dlg(dlg):
        dlg.open = False
        page.update()

    def do_reset(dlg):
        nonlocal team
        dlg.open = False
        page.overlay.clear()
        reset_game()
        team = Team()
        page.clean()
        show_start()

    if team and team.name:
        show_garage()
    else:
        show_start()


ft.app(target=main)
