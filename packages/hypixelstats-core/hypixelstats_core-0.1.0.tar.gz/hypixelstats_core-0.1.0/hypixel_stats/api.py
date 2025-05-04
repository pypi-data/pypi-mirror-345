import requests
from .exceptions import APIKeyError, PlayerNotFoundError

def get_uuid(username: str) -> str:
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 204:
        raise ValueError(f"Username '{username}' not found")
    elif response.status_code != 200:
        raise ConnectionError(f"Failed to get UUID: {response.status_code}")

    data = response.json()
    return data["id"]

def get_player_data(api_key: str, username: str) -> dict:
    uuid = get_uuid(username)

    url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
    headers = {
        "User-Agent": "hypixel-stats-module",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ConnectionError(f"Failed to connect to Hypixel API: {response.status_code}")

    data = response.json()

    if not data.get("success", False):
        raise APIKeyError("Invalid API key or rate limit exceeded.")

    if data.get("player") is None:
        raise PlayerNotFoundError(f"Player '{username}' not found.")

    return data["player"]