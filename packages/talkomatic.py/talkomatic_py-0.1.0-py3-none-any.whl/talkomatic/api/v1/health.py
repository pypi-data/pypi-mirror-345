from requests import get as requests_get

from dataclasses import dataclass


@dataclass
class ServerHealth:
    """
    A class representing the Talkomatic server uptime.

    Args:
        status (bool): Whether the server is up.
        uptime (float): The uptime of the server.
        since_timestamp (float): The timestamp of when the server was last restarted.
        server_version (str): The version of the server.
    """

    status: bool
    uptime: float | None
    since_timestamp: float | None
    server_version: str | None
    
    @classmethod
    def get(cls) -> "ServerHealth":
        response = requests_get("https://classic.talkomatic.co/api/v1/health")
        if response.status_code != 200: 
            return cls(
                status = False,
                uptime = None,
                since_timestamp = None,
                server_version = None
            )
        data = response.json()

        return cls(
            status = True,
            uptime = data["uptime"],
            since_timestamp = data["timestamp"],
            server_version = data["version"]
        )

__all__ = ["ServerHealth"]
