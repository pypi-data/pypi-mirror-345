"""
talkomatic.py

An easy-to-use Python versatile wrapper for the Talkomatic Bot interface ensuring best practices for making bots, and handling the REST API.
"""


from .bot import Bot
from .commands import *
from .dataclasses import *

from talkomatic import api
import talkomatic.bot
import talkomatic.commands
import talkomatic.dataclasses

__all__ = [
    "api",
    "bot",
    "dataclasses",
    "Bot",
    "Room",
    "RoomType",
    "RoomLayoutType",
    "User",
    "RateLimits",
    "DISABLE_RATE_LIMITS"
]
__author__  = "BatteRaquette581 & the talkomatic.py GitHub contributors"
__license__ = "MIT"
__version__ = "0.1.0"
__title__   = "talkomatic.py"
