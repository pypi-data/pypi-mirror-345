NORMAL_MODES = {
    "solo": "eight_one_",
    "doubles": "eight_two_",
    "threes": "four_three_",
    "fours": "four_four_",
    "4v4": "two_four_"
}

DREAM_MODES = {
    "rush": "rush_",
    "ultimate": "ultimate_",
    "lucky": "lucky_",
    "castle": "castle_",
    "voidless": "voidless_",
    "swap": "swap_",
    "dream": "dream_"
}

def get_stat(player_data: dict, mode: str = None) -> dict:
    stats = player_data.get("stats", {}).get("Bedwars", {})
    mode = mode.lower() if mode else None

    if mode in NORMAL_MODES:
        prefix = NORMAL_MODES[mode]
    elif mode in DREAM_MODES:
        prefix = DREAM_MODES[mode]
    elif mode is None:
        prefix = ""
    else:
        raise ValueError(f"Unknown BedWars mode: {mode}")

    def get(key): return stats.get(prefix + key, 0)

    return {
        "mode": mode or "overall",
        "level": stats.get("Experience", 0) // 5000,
        "wins": get("wins_bedwars"),
        "losses": get("losses_bedwars"),
        "kills": get("kills_bedwars"),
        "deaths": get("deaths_bedwars"),
        "beds_broken": get("beds_broken_bedwars"),
        "games_played": get("games_played_bedwars")
    }
