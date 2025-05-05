from talkomatic.dataclasses import Room, RoomType, RoomLayoutType
from .api_key import auth_headers

from requests import get as requests_get
from requests import post as requests_post

from enum import Enum


def get_rooms() -> list[Room]:
    """
    Get all visible (public/semi-private) rooms from the Talkomatic REST API.

    Returns:
        list[Room]: A list of all visible rooms.
    """

    rooms = requests_get("https://classic.talkomatic.co/api/v1/rooms", headers = auth_headers).json()
    return [Room.from_raw_json(room) for room in rooms]

def get_room(room_id: int) -> Room:
    """
    Get a room (including private rooms) from the Talkomatic REST API by ID.

    Args:
        room_id (int): The ID of the room.

    Returns:
        Room: The room with the given ID.
    """

    room = requests_get(f"https://classic.talkomatic.co/api/v1/rooms/{room_id}", headers = auth_headers).json()
    return Room.from_raw_json(room)

def create_room(room_name: str, room_type: RoomType, layout: RoomLayoutType) -> int:
    """
    Create a room on the Talkomatic REST API with its name, type and layout.

    Args:
        room_name (str): The name of the room.
        room_type (RoomType): The type of the room.
        layout (RoomLayoutType): The layout of the room.

    Returns:
        int: The ID of the created room.
    """

    response = requests_post(f"https://classic.talkomatic.co/api/v1/rooms", headers = auth_headers, json = {
        "name": room_name,
        "type": room_type.value,
        "layout": layout.value
    })
    if response.status_code != 200: raise RuntimeError("Failed to create room.")
    return int(response.json()["roomId"])

class RoomJoinStatus(Enum):
    """
    A class representing the error codes for can_join_room
    API endpoint.
    """

    SUCCESS          = "ok"
    NOT_FOUND        = "NOT_FOUND"
    ROOM_FULL        = "ROOM_FULL"
    FORBIDDEN        = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SERVER_ERROR     = "SERVER_ERROR"

def can_join_room(room_id: int, access_code: int | None = None) -> RoomJoinStatus:
    """
    Check if a room can be joined by the user.

    Args:
        room_id (int): The ID of the room.
        access_code (int, optional): The access code of the room.
    
    Returns:
        bool: Whether the room can be joined.
    """

    response = requests_post(f"https://classic.talkomatic.co/api/v1/rooms/{room_id}/join", headers = auth_headers, json = {
        "accessCode": str(access_code) if access_code else None
    })
    if response.status_code == 200: return RoomJoinStatus.SUCCESS
    else: return RoomJoinStatus(response.json()["error"]["code"])

__all__ = ["get_rooms", "get_room", "create_room", "can_join_room", "RoomJoinStatus"]
