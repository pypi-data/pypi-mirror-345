SKYWARS_MODES = {
    "solo_normal": "_solo_normal",
    "solo_insane": "_solo_insane",
}

def calculate_skywars_level(exp: int) -> int:
    if exp < 20:
        return 1
    elif exp < 70:
        return 2
    elif exp < 150:
        return 3
    elif exp < 250:
        return 4
    return 5 + (exp - 250) // 100

def get_stat(player_data: dict, mode: str = None) -> dict:
    stats = player_data.get("stats", {}).get("SkyWars", {})
    mode = mode.lower() if mode else None

    if mode in SKYWARS_MODES:
        prefix = SKYWARS_MODES[mode]
    elif mode is None:
        exp = stats.get("skywars_experience", 0)
        level = calculate_skywars_level(exp)
        return {
            "mode": "overall",
            "level": level,
            "wins": stats.get("wins", 0),
            "losses": stats.get("losses", 0),
            "kills": stats.get("kills", 0),
            "deaths": stats.get("deaths", 0),
            "souls": stats.get("souls", 0),
            "coins": stats.get("coins", 0),
            "games_played": stats.get("games_played_skywars", 0),
        }
    else:
        raise ValueError(f"Unknown SkyWars mode: {mode}")

    def get(key): return stats.get(key + prefix, 0)

    return {
        "mode": mode,
        "wins": get("wins"),
        "losses": get("losses"),
        "kills": get("kills"),
        "deaths": get("deaths"),
    }
