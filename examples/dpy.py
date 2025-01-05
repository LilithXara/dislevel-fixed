from databases import Database
from discord import Intents
from discord.ext import commands

from dislevel import init_dislevel
from dislevel.utils import update_xp

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    db = Database("sqlite:///leveling.db")
    await db.connect()

    await init_dislevel(bot, db, "databases")
    await bot.load_extension("dislevel.discord")
    print("Ready! Let's go...")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await update_xp(bot, message.author.id, message.guild.id, amount=10)
    await bot.process_commands(message)


@bot.event
async def on_dislevel_levelup(guild_id, member_id, level):
    print(guild_id, member_id, level)


TOKEN: str = "Your Token Here"
bot.run(TOKEN)
