MURDER_MODES = {
    "classic": "_MURDER_CLASSIC",
    "double-up": "_MURDER_DOUBLE_UP",
}

def get_stat(player_data: dict, mode: str = None) -> dict:
    stats = player_data.get("stats", {}).get("MurderMystery", {})
    mode = mode.lower() if mode else None

    if mode in MURDER_MODES:
        prefix = MURDER_MODES[mode]
    elif mode is None:
        prefix = ""
    else:
        raise  ValueError(f"Unknown MurderMystery mode: {mode}")

    def get(key): return stats.get(key + prefix, 0)

    return {
        "mode": mode or "overall",
        "wins": get("wins"),
        "deaths": get("deaths"),
        "kills": get("kills"),
        "kills_as_murderer": get("kills_as_murderer"),
        "knife kills": get("knife_kills"),
        "bow kills": get("bow_kills"),
        "was hero": get("was_hero"),
        "game_played": get("games"),
    }