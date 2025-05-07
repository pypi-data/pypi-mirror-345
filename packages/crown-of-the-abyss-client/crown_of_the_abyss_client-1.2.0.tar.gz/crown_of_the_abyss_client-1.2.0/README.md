# Crown of the Abyss

## Description
Crow of the Abyss is a multiplayer, turn-based dungeon crawler.

The player(s) may move around the dungeon, fight enemy, purchase tools, and earn the crown.

## Player Types
All player types have a base stats consisting of:

 - Damage (DG): Base damage of weapons.
 - Armor (AR): Reduces damage received.
 - Magic (MG): Base damage of magic weapons/items.
 - Health (HP): Can withstand more damage.
 - Speed (SP): Higher chance of evading attacks and attacking first.
 - Luck (LK): Non-enemy rooms have a higher chance of being more rewarding.
  

| Archetypes      | Description         | DG  | AR  | MG  | HP  | SP  | LK  |
|-----------------|---------------------|-----|-----|-----|-----|-----|-----|
| Warrior         | Melee specialist     |↑|↑|↓|-|-|-|
| Mage            | Master of magic      |-|↓|↑|↓|-|-|
| Rogue           | Stealth and agility  |-|-|↓|-|↑|↑|
| Tank         | Stalwart defender   |↓|↑|↓|↑|↓|-|
| Cleric          | Healer and support   |-|↓|↑|-|↑|↓|

## Room Types

- Normal: A normal room, that does nothing.
- Shop: A room with a merchant.
- Enemy: A room with enemies.
- Boss: The final room of the dungeon.

## Multiplayer

Multiplayer allows teams to make more diverse experiences in Crown of the Abyss. 
However, the more players in your party, the more difficult the dungeon will be. Players can trade items and currency amongst each other.
Players can view each others health at any point in the game. During battles, players can also view the order of events with players
and enemies.

## Game Architecture

### System Architecture
![crown-of-the-abyss-architecture](./crown-of-the-abyss-architecture.jpg)

The game uses a FastAPI hub server to manage use interactions, a FastAPI REST API to send and receive persistent data to a SQLite database. The game client holds all the game assets to reduce latency among server and other users.

### Database Architecture
![crown-of-the-abyss-database-tables](./drawSQL-image-export-2025-05-06.png)

A ER (Entity Relation) diagram displaying relations among resources and data in the database for The Crown of the Abyss.

### Client and Hub Server Loops 

The hub server and client are connected via Websockets. This means they are sending many messages back and forth.
The loop of each of them can be shown as:

### Client
![crown-of-the-abyss-client-loop](./Cotb-client.png)

### Hub Server
![crown-of-the-abyss-server-loop](./Cotb-server.drawio.png)

## Resources

### Assets Creation

...

### Technical Libraries
- [Pygame](https://www.pygame.org/) - A cross-platform set of Python modules designed for writing video games and multimedia applications.
- [websockets](https://websockets.readthedocs.io/) - A library for building WebSocket servers and clients in Python with asyncio support.
- [Requests](https://docs.python-requests.org/en/latest/) - A simple and elegant HTTP library for sending HTTP/1.1 requests with Python.
- [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) - A built-in Python module that provides a lightweight, disk-based database using the SQLite database engine.
- [Uvicorn](https://www.uvicorn.org/) - A lightning-fast ASGI server implementation, using `uvloop` and `httptools`.
- [Docker](https://www.docker.com/) - A platform for developing, shipping, and running applications in isolated containers.
- [Sphinx](https://www.sphinx-doc.org/) - A tool that makes it easy to create intelligent and beautiful documentation for Python projects.
