import requests


def get_public_ip() -> str:
    return requests.get("https://checkip.amazonaws.com").text.strip()
