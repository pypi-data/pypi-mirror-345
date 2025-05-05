from .api.v1 import ServerConfig, can_join_room, RoomJoinStatus
from .commands import Command, CommandParameter
from .dataclasses import *

from socketio import AsyncClient

from asyncio import run as async_run
from asyncio import sleep as async_sleep
from time import time
from typing import Callable, Awaitable, Any


_server_config = ServerConfig.get()
Binding = Callable[..., Awaitable[Any]] | None

class Bot:
    """
    A wrapper class around the socket.io Talkomatic API. This bot uses
    an asynchronous socket.io client to optimize for concurrency,
    while abstracting error handling, disconnecting, and other low-level
    details, to make writing bots easier.

    Args:
        username (str): The username of the bot.
        location (str): The location of the bot.
        The bot's name will show up as "username / location".

        Optional:
        rate_limits (RateLimits): The rate limits of the bot. (disabled by default to make
        development easier, consider putting rate limits in to prevent getting blocked by the API)
        debug (bool): Whether to enable debug mode for the internal socket.io
        client. Defaults to False.
    """

    sio: AsyncClient
    rate_limits: RateLimits
    user: User
    current_room: Room | None= None
    commands: dict[str, Command] = {}
    command_marker: str
    rooms: list[Room] = []
    user_database: dict[str, User] = {}
    user_messages: dict[User, str] = {}
    _fully_started: bool = False

    on_connect_binding               : Binding = None
    on_room_creation_binding         : Binding = None
    on_inactivity_disconnect_binding : Binding = None
    on_room_join_binding             : Binding = None
    on_room_leave_binding            : Binding = None
    on_user_message_binding          : Binding = None
    on_user_join_binding             : Binding = None
    on_user_leave_binding            : Binding = None
    on_user_vote_binding             : Binding = None

    _time_since_last_message: float = 0
    _time_since_last_room_join: float = 0
    _time_since_last_room_creation: float = 0

    def __init__(self, command_marker: str = "/", rate_limits: RateLimits = DISABLE_RATE_LIMITS, debug: bool = False) -> None:
        self.sio = AsyncClient(engineio_logger = debug, logger = debug)
        self.rate_limits = rate_limits
        self.command_marker = command_marker

    def run(self, username: str, location: str, create_help_command: bool = False) -> None:
        """
        Runs the bot.

        Args:
            username (str): The username of the bot.
            location (str): The location of the bot.
        """

        assert len(username) <= _server_config.max_username_length, f"Username must be less (or equal) than {_server_config.max_username_length} characters."
        assert len(location) <= _server_config.max_location_length, f"Location must be less (or equal) than {_server_config.max_location_length} characters."

        if create_help_command:
            @self.command(
                name = "help",
                description = "Shows this help menu.",   
                parameters = [
                    CommandParameter(
                        "command_name",
                        "The command to get help for.",
                        str,
                        positional = True,
                        required = False
                    )
                ]
            ) # type: ignore
            async def _help_command(user: User, command_name: str | None = None) -> None:
                message = ""
                if command_name:
                    command = self.commands.get(command_name)
                    if command:
                        if not command.hidden:
                            message += f"{self.command_marker}{command_name} - {command.description}\n"
                            for parameter in command.parameters:
                                message += f"    {'' if parameter.positional else '--'}{parameter.name} - {parameter.description} ({parameter.data_type.__name__}){'' if parameter.required else ' [optional]'}\n"
                        else:
                            message += f"Command '{self.command_marker}{command_name}' not found."
                    else:
                        message += f"Command '{self.command_marker}{command_name}' not found."
                else:
                    for command_name, command in self.commands.items():
                        if not command.hidden:
                            message += f"   {', '.join([self.command_marker + alias for alias in [command.name] + command.aliases])} - {command.description}\n"
                await self.send_message(message)

        try:
            async_run(self._run(username, location))
        except KeyboardInterrupt:
            print("\033[1;33mCtrl+C pressed, disconnecting...\033[0m")
            async_run(self.disconnect())

    async def _run(self, username: str, location: str) -> None:
        await self.sio.connect("https://classic.talkomatic.co/")
        await self._join_lobby(username, location)
        self.sio.on("signin status", self._signin_status)
        await self.sio.emit("check signin status")

        def _bind_event_ignore_args(event_name: str, binding: Binding) -> None:
            if binding:
                async def _(*_) -> None:
                    await binding()
                self.sio.on(event_name, _)

        def _bind_room_created(binding: Binding) -> None:
            if binding:
                async def _(room_id: str) -> None:
                    await binding(int(room_id))
                self.sio.on("room created", _)

        self.sio.on            ("lobby update", self._lobby_update)
        self.sio.on            ("chat update",  self._chat_update)
        _bind_event_ignore_args("connect",      self.on_connect_binding)
        _bind_room_created     (                self.on_room_creation_binding)
        self.sio.on            ("room joined",  self._room_join)
        self.sio.on            ("room update",  self._room_update)
        self.sio.on            ("user joined",  self._user_join)
        self.sio.on            ("user left",    self._user_leave)
        self.sio.on            ("update votes", self._update_votes)
        self.sio.on            ("error",        self._error)
        while not self._fully_started:
            await async_sleep(0.01) # HACK

        if self.on_connect_binding:
            await self.on_connect_binding()

        await self.sio.wait()
        await self.disconnect()
    
    async def _chat_update(self, data: dict) -> None:
        user = self.get_user_by_id(data["userId"])
        if user == None:
            user = User(data["userId"], data["username"], "", id_only = True) # i have serious beef with mohd.
        if user not in self.user_messages:
            self.user_messages[user] = ""
        
        diff = data["diff"]
        if diff["type"] == "full-replace":
            self.user_messages[user] = diff["text"]
        elif diff["type"] == "add":
            self.user_messages[user] = self.user_messages[user][:diff["index"]] + diff["text"] + self.user_messages[user][diff["index"]:]
        elif diff["type"] == "delete":
            self.user_messages[user] = self.user_messages[user][:diff["index"]] + self.user_messages[user][diff["index"] + diff["count"]:]
        elif diff["type"] == "replace":
            self.user_messages[user] = self.user_messages[user][:diff["index"]] + diff["text"] + self.user_messages[user][diff["index"] + diff["count"]:]
        else:
            raise RuntimeError(f"Unknown chat update type: {diff['type']}")
        
        if self.commands != {}:
            for command_name, command in self.commands.items():
                if self.user_messages[user].startswith(self.command_marker + command_name):
                    first_line = self.user_messages[user].split("\n")[0]
                    val = await command.execute(user, first_line[len(self.command_marker + command_name):].strip())
                    if val != "":
                        await self.send_message(val)
     
        if self.on_user_message_binding:
            await self.on_user_message_binding(user, self.user_messages[user])

    async def _error(self, data: dict) -> None:
        error = data["error"]
        if error["code"] == "ACCESS_DENIED" and error["message"] == "Disconnected due to inactivity":
            self.current_room = None
            self.user_messages = {}
            if self.on_inactivity_disconnect_binding:
                await self.on_inactivity_disconnect_binding()
        else:
            print(f"Uncaught error socket.io event: {error}")

    async def _join_lobby(self, username: str, location: str) -> None:
        await self.sio.emit("join lobby", {
            "username": username,
            "location": location
        })
    
    async def _lobby_update(self, rooms_data: list[dict]) -> None:
        rooms = [Room.from_raw_json(room_data) for room_data in rooms_data]
        self.rooms = rooms
        
        for room in self.rooms:
            for user in room.users:
                self.user_database[user.id] = user
        
        self._fully_started = True
    
    async def _signin_status(self, data: dict) -> None:
        self.user = User.from_raw_json(data)
    
    async def _room_join(self, data: dict) -> None:
        self.current_room = Room.from_raw_json(data)
        lobby_room_info = self.get_room_by_id(self.current_room.room_id)
        if lobby_room_info != None: # private room, we can't really do anything about it
            self.current_room.banned_users = lobby_room_info.banned_users
            self.current_room.last_time_active = lobby_room_info.last_time_active
            self.current_room.is_full = lobby_room_info.is_full
        self.user_messages = {self.get_user_by_id(user_id): message for user_id, message in data["currentMessages"].items()} # type: ignore

        if self.on_room_join_binding:
            await self.on_room_join_binding(self.current_room)
    
    async def _room_update(self, data: dict) -> None:
        self.current_room = Room.from_raw_json(data)
        
    async def _user_join(self, data: dict) -> None:
        if self.current_room == None:
            return # we just wait for room update event to do the job
        
        user = User.from_raw_json(data)
        self.current_room.users.append(user)
        self.user_messages[user] = ""

        if self.on_user_join_binding:
            await self.on_user_join_binding(user)
    
    async def _user_leave(self, data: str) -> None:
        if self.current_room == None: return
        for user in self.current_room.users:
            if user.id == data:
                self.current_room.users.remove(user)
                if user in self.user_messages:
                    del self.user_messages[user]
                if self.on_user_leave_binding:
                    await self.on_user_leave_binding(user)
                return
    
    async def _update_votes(self, data: dict) -> None:
        if self.current_room == None: return
        if self.current_room.votes == None: return
        new_votes = Room._parse_votes({
            "votes": data,
            "users": self.current_room.users
        })

        # get voted and voter, and whether the voted was added or removed
        if new_votes == {}:
            if not self.current_room.votes:
                return
            voted = list(self.current_room.votes.keys())[0]
            voter = self.get_user_by_id(self.current_room.votes[voted][0].id)
            voted = self.get_user_by_id(voted.id)
            self.current_room.votes = new_votes
            if self.on_user_vote_binding:
                await self.on_user_vote_binding(voter, voted, False)
        else:
            for voted, voters in new_votes.items():
                old_voters = self.current_room.votes.get(voted, [])
                for voter in voters:
                    if voter not in old_voters:
                        if self.on_user_vote_binding:
                            self.current_room.votes = new_votes
                            await self.on_user_vote_binding(
                                self.get_user_by_id(voter.id),
                                self.get_user_by_id(voted.id),
                                True
                            )
                            return
                for voter in old_voters:
                    if voter not in voters:
                        if self.on_user_vote_binding:
                            self.current_room.votes = new_votes
                            await self.on_user_vote_binding(
                                self.get_user_by_id(voter.id),
                                self.get_user_by_id(voted.id),
                                False
                            )
                            return
    
    def command(
        self,
        name: str,
        description: str = "",
        parameters: list[CommandParameter] = [],
        aliases: list[str] = [],
        hidden: bool = False
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
        """
        Decorator for registering commands.

        Args:
            name (str): The name of the command.
            description (str): The description of the command.
            parameters (list[CommandParameter]): The parameters of the command.
            aliases (list[str]): The aliases of the command.
            hidden (bool): Whether the command will show up in the built-in /help command.
        """

        def register_command(function: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            command = Command(name, description, aliases, hidden)
            command.function = function
            for parameter in parameters:
                command.add_argument(
                    [parameter.name] + parameter.aliases,
                    parameter.description,
                    parameter.data_type,
                    parameter.positional,
                    parameter.required,
                    parameter.number_of_args
                )
            command.parameters = parameters
            self.commands[name] = command
            return function
        return register_command
    
    async def create_room(self, room_name: str, room_type: RoomType = RoomType.PUBLIC, room_layout: RoomLayoutType = RoomLayoutType.VERTICAL, room_password: int | None = None) -> bool:
        """
        Creates a room with the given name, type, layout, and password.

        Args:
            room_name (str): The name of the room.
            room_type (RoomType): The type of the room.
            room_layout (RoomLayoutType): The layout of the room.
            room_password (int, **must be 6 digits**): The password of the room (if the room is not public).
        
        Returns:
            bool: Whether the room was created successfully (returns False if the room was
            not created due to rate limits).
        """

        if time() - self._time_since_last_room_creation < self.rate_limits.room_creation_cooldown:
            return False

        if room_password != None:
            assert 100000 <= room_password <= 999999, "Room password must be a 6 digits integer."
        
        assert len(room_name) <= _server_config.max_room_name_length, f"Room name must be less (or equal) than {_server_config.max_room_name_length} characters."

        await self.sio.emit("create room", {
            "name": room_name,
            "type": room_type.value,
            "layout": room_layout.value,
            "accessCode": str(room_password) if room_password != None else ""
        })
        return True
    
    async def disconnect(self) -> None:
        """
        Disconnects the bot from the server.
        """

        await self.sio.disconnect()
    
    def get_room_by_id(self, id: int) -> Room | None:
        """
        Gets a room by its ID.
        Returns None if the room does not exist.

        Args:
            id (int): The ID of the room to get.

        Returns:
            Room: The room object. (None if the room does not exist)
        """

        for room in self.rooms:
            if room.room_id == id:
                return room
        return None
    
    def get_user_by_id(self, id: str) -> User | None:
        """
        Allows you to get a user from the user database by their ID.
        Useful for getting a user from a "id-only" user, but is not
        guaranteed to work if the user is not in a room anymore.
        
        Args:
            id (str): The ID of the user to get.

        Returns:
            User: The full user object. (None if the user is not in the database)
        """

        return self.user_database.get(id)
    
    def get_user_message(self, user: User) -> str:
        """
        Gets the message of a user.

        Args:
            user (User): The user to get the message of.

        Returns:
            str: The message of the user.
        """

        return self.user_messages.get(user, "")
    
    async def join_room(self, room: Room | int, access_code: int | None = None, do_api_check: bool = True) -> bool:
        """
        Joins a room with the given room/room ID and access code.
        **Reminder: your bot can only be in 1 room at a time!**

        Args:
            room (Room | int): The room (or ID of the room) to join.
            access_code (int | None): The 6 digit access code of the room to join (if the room is not public).
            do_api_check (bool): Whether to check if the room can be joined using the Talkomatic API.
        
        Returns:
            bool: Whether the room was joined successfully (returns False if the room was
            not joined due to rate limits).
        """

        if time() - self._time_since_last_room_join < self.rate_limits.room_join_cooldown:
            return False

        if isinstance(room, int):
            room_id = room
        else:
            room_id = room.room_id

        if do_api_check:
            status = can_join_room(room_id, access_code)
            if status != RoomJoinStatus.SUCCESS:
                raise RuntimeError(f"Failed to join room {room_id}: {status}")

        await self.sio.emit("join room", {
            "roomId": str(room_id),
            "accessCode": str(access_code) if access_code != None else None
        })
        return True
    
    async def leave_room(self) -> None:
        """
        Leaves the room the bot is currently in.
        """

        await self.sio.emit("leave room")

    def on_connect(self, binding: Binding) -> Binding:
        """
        Binds a function to when the bot finishes connection to the server.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_connect_binding = binding
        return binding

    def on_inactivity_disconnect(self, binding: Binding) -> Binding:
        """
        Binds a function to when the bot is disconnected due to having not interacted for too long.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_inactivity_disconnect_binding = binding
        return binding

    def on_room_creation(self, binding: Binding) -> Binding:
        """
        Binds a function to when the bot has successfully created the room.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_room_creation_binding = binding
        return binding

    def on_room_join(self, binding: Binding) -> Binding:
        """
        Binds a function to when the bot has successfully joined the room.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_room_join_binding = binding
        return binding

    def on_room_leave(self, binding: Binding) -> Binding:
        """
        Binds a function to when the bot has successfully left the room.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_room_leave_binding = binding
        return binding

    def on_user_message(self, binding: Binding) -> Binding:
        """
        Binds a function to when a user sent a message in the bot's current room.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_user_message_binding = binding
        return binding

    def on_user_join(self, binding: Binding) -> Binding:
        """
        Binds a function to when another user has joined the bot's current room.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_user_join_binding = binding
        return binding

    def on_user_leave(self, binding: Binding) -> Binding:
        """
        Binds a function to when a user has left the bot's current room.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_user_leave_binding = binding
        return binding

    def on_user_vote(self, binding: Binding) -> Binding:
        """
        Binds a function to when a user has voted to a ban another user from the bot's current room.

        Args:
            binding (Coroutine): The function to bind to the event.
        """

        self.on_user_vote_binding = binding
        return binding
    
    async def send_message(self, message: str) -> bool:
        """
        Sends the message to the room the bot is currently in.

        Args:
            message (str): The message to send.
        
        Returns:
            bool: Whether the message was sent successfully (returns False if the message was
            not sent due to rate limits).
        """

        assert len(message) <= _server_config.max_message_length, f"Message is too long, max length is {_server_config.max_message_length} characters."

        if time() - self._time_since_last_message < self.rate_limits.message_cooldown:
            return False

        await self.sio.emit("chat update", {
            "diff": {
                "type": "full-replace",
                "text": message
            }
        })
        return True
    
    async def toggle_vote(self, user: User) -> None:
        """
        Votes the user to be banned (or remove vote if the user is already voted by the bot)
        from the room the bot is currently in.

        Args:
            user (User): The user to vote for.
        """

        await self.sio.emit("vote", {
            "targetUserId": user.id
        })


__all__ = ["Bot"]
