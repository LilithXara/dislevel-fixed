# Dislevel (Fork by Lilith Vala Xara)

A modernized fork of the Dislevel project, fixing longstanding issues like the broken `/leaderboard` command, and ensuring seamless leveling functionality for Discord bots. Whether you're running a small bot or managing a large community, this updated version works out of the box.

## Key Features

- Fully functional `/leaderboard` command.
- Easy integration with `discord.py` or `nextcord`.
- Supports both standard and slash commands.
- Works with modern database drivers (`asyncpg`, `databases`).

**Last Updated: November 22, 2024**

---

## Installation

```bash
pip install dislevel
```

---

## Usage

Dislevel requires a database connection to track user levels. It supports two types of database connections:

- `asyncpg (Pool)`
- `databases (Database)`

If your bot already has a database connection, you can use it with Dislevel. Otherwise, you can create a new connection. Below is an example of creating a simple bot with a SQLite database.

### Example Code

```python
from databases import Database
from discord import Intents
from discord.ext import commands

from dislevel import init_dislevel
from dislevel.utils import update_xp

intents = Intents.default()

# For discord.py, enable message content explicitly if required.
# intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    # Initialize a SQLite database connection using `databases`.
    db = Database("sqlite:///leveling.db")
    await db.connect()

    # Pass the bot instance, database connection, and driver type to initialize Dislevel.
    await init_dislevel(bot, db, "databases")
    print("Bot is ready and Dislevel is initialized!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Update XP for the user. Pass bot, user ID, guild ID, and XP amount.
    await update_xp(bot, message.author.id, message.guild.id, amount=10)

    await bot.process_commands(message)


# Load Dislevel's cog for standard commands (supports both `discord.py` and `nextcord`).
bot.load_extension("dislevel.discord")

TOKEN: str = "Your bot token here"
bot.run(TOKEN)
```

---

## Events

Want to add custom behavior when a user levels up? You can use the `on_dislevel_levelup` event:

```python
async def on_dislevel_levelup(guild_id, member_id, level):
    print(f"User {member_id} in guild {guild_id} leveled up to {level}!")
```

---

## Cogs

Dislevel provides different cogs depending on your framework and command type:

- `dislevel.discord`: Standard commands for `discord.py` 2.0.
- `dislevel.discord.slash`: Slash commands for `discord.py` 2.0.
- `dislevel.nextcord`: Standard commands for `nextcord` 2.0.
- `dislevel.nextcord.slash`: Slash commands for `nextcord` 2.0.

---

## Commands

- **`rank [member]`**: View your or another member's rank.
- **`leaderboard` (or `lb`)**: View the leaderboard. (Fixed in this fork!)
- **`setbg <url>`**: Set a custom background URL for your rank card.
- **`resetbg`**: Reset the rank card background to the default.

---

## Why This Fork?

The original Dislevel project had critical issues, particularly the broken `/leaderboard` command, which rendered it impractical for many use cases. This fork by **Lilith Vala Xara** restores full functionality, updates compatibility with modern Discord libraries, and ensures it meets the needs of today’s bots.

---

## Support

- Join the Discord community for help and discussion: [Thelema Discord Server](http://discord.gg/thelema)
- Explore my GitHub for other projects: [Lilith Vala Xara on GitHub](https://github.com/LilithXara)
