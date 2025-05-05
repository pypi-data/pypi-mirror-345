from requests import get as requests_get

from dataclasses import dataclass


@dataclass
class ServerConfig:
    """
    A class representing the Talkomatic server configuration.

    Composed of:
    - max_username_length: The maximum length of a username.
    - max_afk_time: The maximum time for inactivity before the user gets kicked (in milliseconds).
    - max_location_length: The maximum length of a location.
    - max_room_name_length: The maximum length of a room name.
    - max_message_length: The maximum length of a message.
    - max_room_capacity: The maximum number of users in a room.
    - max_connections_per_ip: The maximum number of connections per IP.
    - socket_max_requests_window: The maximum number of requests per window.
    - socket_max_requests_per_window: The maximum number of requests per window.
    - chat_update_rate_limit: The maximum number of chat updates per minute.
    - typing_rate_limit: The maximum number of typing updates per minute.
    - connection_delay: The delay in milliseconds between a user connecting and the first chat update.
    - word_filter_enabled: Whether the word filter is enabled.
    - api_version: The version of the API.
    - server_version: The version of the server.
    """

    max_username_length: int
    max_afk_time: int
    max_location_length: int
    max_room_name_length: int
    max_message_length: int
    max_room_capacity: int
    max_connections_per_ip: int
    socket_max_requests_window: int
    socket_max_requests_per_window: int
    chat_update_rate_limit: int
    typing_rate_limit: int
    connection_delay: int
    word_filter_enabled: bool
    api_version: str
    server_version: str
    
    @classmethod
    def get(cls) -> "ServerConfig":
        response = requests_get("https://classic.talkomatic.co/api/v1/config")
        if response.status_code != 200: raise RuntimeError("The talkomatic.co server is down.")
        data = response.json()
        limits = data["limits"]
        features = data["features"]
        versions = data["versions"]

        return cls(
            max_username_length = limits["MAX_USERNAME_LENGTH"],
            max_afk_time = limits["MAX_AFK_TIME"],
            max_location_length = limits["MAX_LOCATION_LENGTH"],
            max_room_name_length = limits["MAX_ROOM_NAME_LENGTH"],
            max_message_length = limits["MAX_MESSAGE_LENGTH"],
            max_room_capacity = limits["MAX_ROOM_CAPACITY"],
            max_connections_per_ip = limits["MAX_CONNECTIONS_PER_IP"],
            socket_max_requests_window = limits["SOCKET_MAX_REQUESTS_WINDOW"],
            socket_max_requests_per_window = limits["SOCKET_MAX_REQUESTS_PER_WINDOW"],
            chat_update_rate_limit = limits["CHAT_UPDATE_RATE_LIMIT"],
            typing_rate_limit = limits["TYPING_RATE_LIMIT"],
            connection_delay = limits["CONNECTION_DELAY"],
            word_filter_enabled = features["ENABLE_WORD_FILTER"],
            api_version = versions["API"],
            server_version = versions["SERVER"]
        )

__all__ = ["ServerConfig"]
