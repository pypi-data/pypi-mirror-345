from dataclasses import dataclass


@dataclass
class User:
    """
    A class representing a user in a lobby.

    In some places, "id-only users" are used, which are users that only have an ID
    and no username or location attached. These are where the original Talkomatic
    API only specifies a user ID, and not a username or location. You can still
    try retrieving the username and location from the bot if the user is stored
    in the bot's currently online user database, but this is not guaranteed.

    Composed of:
    - id: The user's raw ID in web safe Base64 encoding.
    - username: The user's username. (doesn't apply if the user is a "id-only user")
    - location: The user's location. (doesn't apply if the user is a "id-only user")
    - id_only: Whether the user is an "id-only user".
    """

    id: str
    username: str
    location: str
    id_only: bool

    @classmethod
    def from_raw_json(cls, data: dict, id_only: bool = False) -> "User":
        return cls(
            id = data["id" if "id" in data else "userId"],
            username = data["username"],
            location = data["location"],
            id_only = id_only
        )
    
    @classmethod
    def from_id_only(cls, id: str) -> "User":
        return cls.from_raw_json({"id": id, "username": "", "location": ""}, id_only = True)
    
    def __eq__(self, other: "User") -> bool:
        if not isinstance(other, User):
            return False
        
        return self.id == other.id
    
    def __ne__(self, other: "User") -> bool:
        return not self.__eq__(other)
    
    def __str__(self) -> str:
        return f'User "{self.username} / {self.location}" with id: {self.id}{" (id-only)" if self.id_only else ""}'
    
    def __hash__(self) -> int:
        return hash(self.id)

__all__ = ["User"]
