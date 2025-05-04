def get_stat(player_data: dict, mode: str = None) -> dict:
    stats = player_data.get("stats", {}).get("BuildBattle", {})

    def get(key): return stats.get(key, 0)

    return {
        "mode": "Build Battle",
        "wins": get("wins"),
        "super votes": get("super_votes"),
        "game_played": get("games_played"),
    }