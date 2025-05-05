from dataclasses import dataclass


@dataclass
class RateLimits:
    """
    A class representing the rate limits of bot actions
    (to prevent get blocked by the API).

    The original server's limits are:
    - 1000 requests per minute
    - 30 second cooldown on creating rooms
    - message length and frequency limits

    Composed of:
    - message_cooldown: The cooldown in seconds between messages.
    - room_join_cooldown: The cooldown in seconds between joining rooms.
    - room_creation_cooldown: The cooldown in seconds between creating rooms.
    """

    message_cooldown: float = 0.1
    room_join_cooldown: float = 5
    room_creation_cooldown: float = 30

DISABLE_RATE_LIMITS = RateLimits(message_cooldown = 0, room_join_cooldown = 0, room_creation_cooldown = 0)

__all__ = ["RateLimits", "DISABLE_RATE_LIMITS"]
