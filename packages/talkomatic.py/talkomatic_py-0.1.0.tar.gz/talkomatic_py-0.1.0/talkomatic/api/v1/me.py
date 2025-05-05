from requests import get as requests_get

from dataclasses import dataclass


@dataclass
class UserSession:
    """
    A class representing your current user session's information.

    Args:
        is_signed_in (bool): Whether the user is signed in.
        username (str): The username of the user.
        location (str): The location of the user.
        user_id (str): The ID of the user.
    """

    is_signed_in: bool
    username: str | None
    location: str | None
    user_id: str | None
    
    
    @classmethod
    def get(cls) -> "UserSession":
        response = requests_get("https://classic.talkomatic.co/api/v1/me")
        if response.status_code != 200: raise RuntimeError("The talkomatic.co server is down.")
        data = response.json()

        return cls(
            is_signed_in = data["isSignedIn"],
            username = data["username"] if data["isSignedIn"] else None,
            location = data["location"] if data["isSignedIn"] else None,
            user_id = data["userId"] if data["isSignedIn"] else None
        )

__all__ = ["UserSession"]
