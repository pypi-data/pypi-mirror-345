"""
talkomatic.api.v1

A wrapper for the v1 Talkomatic REST API using dataclasses
to represent the data returned by the API.
"""

from .api_key import auth_headers, valid_api_key
from .config import ServerConfig
from .emoji_list import emoji_list
from .health import ServerHealth
from .me import UserSession
from .offensive_words import WordFilter
from .rooms import get_rooms, get_room, can_join_room, RoomJoinStatus, create_room

__all__ = [
    "RoomJoinStatus",
    "ServerConfig",
    "ServerHealth",
    "UserSession",
    "WordFilter",
    "auth_headers",
    "can_join_room",
    "create_room",
    "emoji_list",
    "get_room",
    "get_rooms",
    "valid_api_key"
]
