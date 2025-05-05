from requests import get as requests_get

from dataclasses import dataclass


@dataclass
class WordFilter:
    """
    A class representing the list of blacklisted words and whitelisted words.

    Contains:
    - offensive_words (list[str]): A list of all the blacklisted strings.
    - whitelisted_words (list[str]): A list of all the strings allowed overriding the blacklisted strings.
    """

    offensive_words: list[str]
    whitelisted_words: list[str]

    @classmethod
    def get(cls) -> "WordFilter":
        response = requests_get("https://classic.talkomatic.co/js/offensive_words.json")
        if response.status_code != 200: raise RuntimeError("Unable to get offensive_words.json.")
        data = response.json()

        return cls(
            offensive_words = data["offensive_words"],
            whitelisted_words = data["whitelisted_words"],
        )

__all__ = ["WordFilter"]
