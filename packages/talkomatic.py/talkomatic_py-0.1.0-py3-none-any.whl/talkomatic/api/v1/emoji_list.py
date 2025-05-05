"""
A dictionary of all the emojis available on the Talkomatic server.

The keys are the emoji names, and the values are the image URLs.
"""

from requests import get as requests_get

response = requests_get("https://classic.talkomatic.co/js/emojiList.json")
if response.status_code != 200: raise RuntimeError("The talkomatic.co server is down.")
emoji_list: dict[str, str] = response.json()

__all__ = ["emoji_list"]
