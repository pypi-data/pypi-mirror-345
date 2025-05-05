"""
talkomatic.dataclasses

A module using classes to represent object like users and rooms in an
intuitive and safe way.
"""

from .rate_limits import RateLimits, DISABLE_RATE_LIMITS
from .room import Room, RoomType, RoomLayoutType
from .user import User

__all__ = ["RateLimits", "DISABLE_RATE_LIMITS", "Room", "RoomType", "RoomLayoutType", "User"]
