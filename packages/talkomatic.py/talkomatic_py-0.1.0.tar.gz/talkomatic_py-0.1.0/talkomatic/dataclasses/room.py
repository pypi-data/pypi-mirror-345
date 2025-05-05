from .user import User

from dataclasses import dataclass
from enum import Enum


class RoomType(Enum):
    """
    The visibility of the room.

    Composed of:
    - PUBLIC: The room is public and can be joined by anyone, with no password required.
    - SEMI_PRIVATE: The room **can be seen** on the room list but can only be joined with a password.
    - PRIVATE: The room **cannot be seen** on the room list and can only be joined with a password.
    """

    PUBLIC = "public"
    SEMI_PRIVATE = "semi-private"
    PRIVATE = "private"

class RoomLayoutType(Enum):
    """
    Whether the textboxes of the user in the room are stacked vertically or horizontally.

    Composed of:
    - VERTICAL: The textboxes of the users in the room are stacked vertically.
    - HORIZONTAL: The textboxes of the users in the room are stacked horizontally.
    """

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

@dataclass
class Room:
    """
    A class representing room information.

    Composed of:
    - room_id (int): The ID of the room.
    - name (str): The name of the room.
    - room_type (RoomType): The type of the room.
    - layout (RoomLayoutType): The layout of the room.
    - users (list[User]): The users in the room.
    - votes (dict[User, list[User]]): The votes in the room.
    - banned_users (list[User]): The banned users in the room.
    - last_time_active (int): The last time the room was active.
    - is_full (bool): Whether the room is full.
    """

    room_id: int
    name: str
    room_type: RoomType
    layout: RoomLayoutType | None
    users: list[User]
    votes: dict[User, list[User]] | None
    banned_users: list[User] | None
    last_time_active: int | None
    is_full: bool | None

    @classmethod
    def _parse_votes(cls, data: dict) -> dict[User, list[User]]:
        # HACK: votes are formatted with {"voted user id": "voter user id"}, we need to reformat them
        # with "id-only" user objects (users only used to compare)
        votes = {}
        for voted_user_id, voter_user_id in data["votes"].items():
            if voted_user_id not in data["users"]:
                votes[voted_user_id] = [voter_user_id]
            else:
                votes[voted_user_id].append(voter_user_id)
        return {User.from_id_only(voted): list(map(User.from_id_only, voters)) for voted, voters in votes.items()}

    @classmethod
    def from_raw_json(cls, data: dict) -> "Room":
        return cls(
            room_id = int(data["id" if "id" in data else "roomId"]),
            name = data["name" if "name" in data else "roomName"],
            room_type = RoomType(data["type" if "type" in data else "roomType"]),
            layout = RoomLayoutType(data["layout"]) if "layout" in data else None,
            users = [User.from_raw_json(user) for user in data["users"]],
            votes = cls._parse_votes(data) if "votes" in data else None,
            banned_users = list(map(User.from_id_only, data["bannedUserIds"])) if "bannedUserIds" in data else None,
            last_time_active = data["lastActiveTime"] if "lastActiveTime" in data else None,
            is_full = data["isFull"] if "isFull" in data else None
        )
    
    def __eq__(self, other: "Room") -> bool:
        if not isinstance(other, Room):
            return False
        
        return self.room_id == other.room_id
    
    def __ne__(self, other: "Room") -> bool:
        return not self.__eq__(other)
    
    def __str__(self) -> str:
        return f"""Room "{self.name}" (id: {self.room_id}):
        - room type: {self.room_type.value}
        - layout: {self.layout if self.layout else "N/A"}
        - users: {", ".join(map(str, self.users))}
        - votes: {", ".join([f"{voted} -> {map(str, voters)}" for voted, voters in self.votes.items()]) if self.votes else "N/A"}
        - banned users: {", ".join(map(str, self.banned_users)) if self.banned_users else "N/A"}
        - last time active (epoch time): {self.last_time_active if self.last_time_active else "N/A"}
        - is full: {self.is_full}"""


__all__ = ["Room", "RoomType", "RoomLayoutType"]
