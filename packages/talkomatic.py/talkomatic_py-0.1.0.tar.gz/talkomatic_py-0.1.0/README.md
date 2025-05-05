# talkomatic.py

An easy-to-use Python versatile wrapper for the Talkomatic Bot interface ensuring best practices for making bots, and handling the REST API.

## Installation
Python 3.8+ is required (to be tested on earlier versions) to use this module.
Optionally, [venv](https://docs.python.org/3/library/venv.html) is recommended to isolate the project's dependencies.

The talkomatic.py can be installed/updated in the shell of your choice with this command:
```bash
python3 -m pip install -U talkomatic.py
```

### Installing the development version / Installing the examples

You can simply clone the repository with git, and install the local module using pip:

```bash
git clone https://github.com/BatteRaquette581/talkomatic.py.git
cd talkomatic.py
python3 -m pip install -U . # if you want to install the dev version
```

Optionally, you can import with the GitHub CLI:

```bash
gh repo clone BatteRaquette581/talkomatic.py
cd talkomatic.py
python3 -m pip install -U . # if you want to install the dev version
```

Or download from an archive (Code > Download ZIP, Releases > [pick your release] > Source code), extract it, and open your command line in the extracted folder:

```bash
python3 -m pip install -U . # if you want to install the dev version
```

To use the examples, see [Using the examples](#using-the-examples).

## Usage

In any python file, the library when installed can be imported with this line:

```python
import talkomatic
```

You can also import only certain parts of the module (like the API) with this:

```python
from talkomatic.api import v1 as api_v1
```

### Using the examples

If you haven't downloaded the examples already, check out this section of the README: [Installing the examples](#installing-the-development-version--installing-the-examples).

At the root folder of the talkomatic.py folder, simply execute the wanted example as a module like this:
```bash
python3 -m examples.[insert example file]
```

For instance, if you want to run the echo.py example:
```bash
python3 -m examples.echo
```

For files in subfolders like the examples/api folder, simply do this:
```bash
python3 -m examples.api.[insert example file]
```

(e.g for examples/api/server_health.py)
```bash
python3 -m examples.api.server_health
```

## Quickstart

### How does talkomatic.py work?

Similar to discord.py, talkomatic.py uses decorators to invoke functions on events/commands:

```python
# the on_room_creation function is invoked when the room is created!
@bot.on_room_creation
async def on_room_creation(room_id: int) -> None:
    print(f"We have successfully created a room with room ID: {room_id}")

# the update_user_list function will both be invoked when:
@bot.on_user_join   # - a user joins the room
@bot.on_user_leave  # - a user leaves the room
async def update_user_list(*args) -> None:
    ...

@bot.command(
    name = "my_command",
    description = "This is a sample command",
    parameters = [
        CommandParameter(
            name = "sample_prompt",
            description = "Sample parameter",
            data_type = str,
            positional = True,
            required = True
        )
    ]
)
async def my_command(user: User, sample_prompt: str) -> None:
    ...
```

As you might have noticed, talkomatic.py works asynchronously.
This means that all events/commands are done in parallel, contrary to synchronous Python, where everything has to wait for one function to finish executing, and only 1 function can execute at a time.
With this, talkomatic.py can better handle users and various events due to concurrency.

Additionally, talkomatic.py uses dataclasses with type-hints to parse inconsistent data formats between events and REST API responses to provide the user with a consistent easy-to-use interface.

### My Room Bot example

```python
from talkomatic import Bot # import the Bot class from the talkomatic package
from talkomatic.dataclasses.room import RoomType, RoomLayoutType 
# we import the RoomType and RoomLayoutType objects to describe the room privacy type, and layout type


bot = Bot() # create a new Bot instance

# with this decorator, the function will be called when the bot finishes connecting to the server
@bot.on_connect
async def on_connect() -> None:
    # we create a room with the name "My awesome room!", it's public, and it's a horizontal layout
    await bot.create_room("My awesome room!", RoomType.PUBLIC, RoomLayoutType.HORIZONTAL)
    # when the room is created, the on_room_creation event will be called

@bot.on_room_creation
async def on_room_creation(room_id: int) -> None:
    # our awesome room has been created, so we'll join it!
    await bot.join_room(room_id)

@bot.on_room_join
async def on_room_join(*args) -> None: # we can put *args because we don't care about the arguments here
    # we joined our awesome room, and it'd be a good idea to greet our fellow users!
    await bot.send_message("""Welcome to my awesome room!

This is an automated message from a bot for the talkomatic.py library!
To the developer of the bot, remember that you can press Ctrl+C in the
terminal to disconnect your bot. :catjam:""")

# we're ready to go! let's run the bot with a username and location
bot.run("My Room", "Bot")
# this'll keep running until you halt the program with ctrl+c!
```

This program creates a bot, that:
- Creates a public room wiht a horizontal layout named "My Awesome Room!" when connected
- Joins it when the room has been created
- And sends a welcome message when the room has been joined
- Creates a bot with username "My Room", and location "Bot" that will connect to the Talkomatic server

Like any talkomatic bot, this can be halted with Ctrl+C.

### Echo bot example

```python
from talkomatic import Bot, CommandParameter, RoomType, User
from talkomatic.commands import INFINITE_ARGS

bot = Bot()

# with this decorator, the function will be called when the bot finishes connecting to the server
@bot.on_connect
async def on_connect() -> None:
    # we find the first non-full public room, we join it, and say "Hello, world!"
    for room in bot.rooms:
        if not room.is_full and room.room_type == RoomType.PUBLIC:
            await bot.join_room(room)
            return
    print("We didn't find any non-full rooms to join. :(") # :(
    await bot.disconnect()

user_messages = {}
async def update_user_messages():
    # we concatenate all the user messages into one message to send
    message = ""
    for user_message in user_messages.values():
        message += f"{user_message}\n"
    await bot.send_message(message)

@bot.command( # this is a decorator that turns the echo function into a command
    name = "echo", # the name of the command
    description = "This command repeats your message!", # the description of the command
    parameters = [ # the parameters of the command
        CommandParameter( # we want a parameter that takes any number of words in the message
            "message", # the name of the parameter
            "The message to repeat.", # the description of the parameter
            str, # the type of the parameter
            positional = True, # the parameter is positional
            required = True, # the parameter is required
            number_of_args = INFINITE_ARGS # the parameter can take any number of words
        )
    ]
)
async def echo(user: User, message) -> None:
    if not isinstance(message, list): # is the user sending a message in the /echo
        if user.id in user_messages: # if 
            del user_messages[user.id]
    else:
        # for each user, we store the message that'll be sent
        user_messages[user.id] = f"{user.username} / {user.location} said: {' '.join(message)}"

    # update the user messages
    await update_user_messages()

@bot.on_user_leave
async def on_user_leave(user: User) -> None:
    if user.id in user_messages: # if they're in one of our user messages dictionary
        del user_messages[user.id] # when a user leaves, we delete them from the user messages
    
    # update the user messages
    await update_user_messages()
    
# we can even make a "hidden" command that doesn't show up in the /help command
@bot.command(name = "ping", hidden = True)
async def ping(user: User) -> None:
    # we can make little easter eggs with this hidden command feature!
    await bot.send_message("Pong!")


bot.run("Echo Bot", "do /help", create_help_command = True) # we let the bot create the help command automatically
```

This bot joins the first available room, and creates a /echo command capable of repeating whatever the users say.
This demonstrates how events and commands can work in conjuction together.

### Using the Talkomatic REST API

Besides the Bot interface, Talkomatic also has a REST API that can be called using GET/POST HTTPS requests.

talkomatic.py has a v1 (latest Talkomatic api version) api wrapper that uses functions and dataclasses with type-hints to abstract the underlying requests and data extracting, to make the Talkomatic REST API easier to use, without needing to worry about handling error codes and API keys.

Here is an example of it to display the public/semi-private rooms in the lobby:
```python
from talkomatic.api.v1 import get_rooms # we import the RoomInfo class from the Talkomatic API module


rooms = get_rooms() # we get the room information using the get method

for room in rooms: # we print all of the rooms!
    print(room)
```

Unlike the Bot interface, this does not use Websockets, and instead uses HTTPS requests.
The Talkomatic REST API provides additional info that cannot be obtained from the Bot interface such as server health (that still works even if the server is down):
```python
from talkomatic.api.v1 import ServerHealth # we import the ServerHealth class from the Talkomatic API module

from datetime import datetime # we import the datetime module to format the uptime


health = ServerHealth.get() # we get the server health using the get method

print(f"Server status: {health.status}") # we print the server status
if health.status:
    uptime = datetime.fromtimestamp(health.uptime).strftime("%H:%M:%S") # we format the uptime
    print(f"Server uptime: {uptime}") # we print the server uptime
    print(f"Server version: {health.server_version}") # we print the server version
```

## Advanced Topics

### ID-only Users

Due to quirks and inconsistencies of how Talkomatic handles users (e.g in votes), there can be users with no username or location specified, and the only way to differentiate them is by user ID (unique to each user, if two user ID's are the same, then the users are the same, `user1.id == user2.id` <=> `user1 == user2`).
This is partially solved by the `Bot.get_user_from_id(user.id)`, that checks if the Bot knows of the user, and returns the full user if it's known, but it is not guaranteed to always work.

### Rate Limits (Alpha)

The Talkomatic server imposes rate limits to Bots sending too many events, to prevent DDOS attacks. 

**Most of the time, you will not need for these, as it is very hard to reach these rate limits with a normal bot not made for reaching those.**

If you still want to have these implemented, talkomatic.py has a solution for it, with the `talkomatic.dataclasses.RateLimits` class.
With this class, you can pass a `rate_limits` argument to the `talkomatic.Bot` class which can tune at what intervals will the bot allow you to perform certain actions:
- Sending messages (default is 0.1 second)
- Joining a room (default is 5 seconds)
- Creating a room (default is 30 seconds)

When using their respective functions with a RateLimits object, those functions will return `False` to signify that the functionality has been rate-limited, and will return `True` otherwise.

The default rate limits are based off of the server rate limits as seen in the [Talkomatic Classic GitHub repository](https://github.com/MohdYahyaMahmodi/talkomatic-classic):
- [0.1 second message sending limit](https://github.com/MohdYahyaMahmodi/talkomatic-classic/blob/main/server.js#L45C1)
- [30 second room creation limit](https://github.com/MohdYahyaMahmodi/talkomatic-classic/blob/main/server.js#L52C1)

### API Reference

There is even more API endpoints, and methods that are not talked about in this README, nor examples, that are available to be seen either in your IDE, or the [online documentation]().

## Credits

Made by BatteRaquette581 and all the GitHub contributors with love <3.
Uses:
- [Python Socket.IO by MiguelGrinberg](https://github.com/miguelgrinberg/python-socketio), and thus [Socket.IO by its contributors](https://github.com/socketio/socket.io) both licensed under [MIT License](https://opensource.org/license/mit).

talkomatic.py was also made thanks to the welcoming [Talkomatic discord community](https://discord.com/invite/N7tJznESrE)!

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit):

```
MIT License

Copyright (c) 2025 BatteRaquette581

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
