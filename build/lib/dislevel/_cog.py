import os
from typing import Optional, Union

from discord import Embed, File, Member, Interaction
from discord.ext import commands
from discord import app_commands
from easy_pil.utils import run_in_executor

from .card import get_card
from .utils import (
    get_leaderboard_data,
    get_member_data,
    get_member_position,
    set_bg_image,
)


class Leveling(commands.Cog):
    """Leveling commands"""

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        self.bot = bot

    @commands.command()
    async def rank(self, ctx: commands.Context, *, member: Optional[Member] = None):
        """Check rank of a user (prefix command)"""
        member = member or ctx.author

        user_data = await get_member_data(self.bot, member.id, ctx.guild.id)
        user_data["position"] = await get_member_position(self.bot, member.id, ctx.guild.id)
        user_data["profile_image"] = str(member.display_avatar.url)

        # Use member attributes directly
        user_data["name"] = member.name
        user_data["descriminator"] = member.discriminator or "0000"  # Default if no discriminator

        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await ctx.send(file=file)

    @app_commands.command(name="rank", description="Check rank of a user (slash command)")
    async def rank_slash(self, interaction: Interaction, member: Optional[Member] = None):
        """Slash command to check rank of a user"""
        member = member or interaction.user

        user_data = await get_member_data(self.bot, member.id, interaction.guild.id)
        user_data["position"] = await get_member_position(self.bot, member.id, interaction.guild.id)
        user_data["profile_image"] = str(member.display_avatar.url)

        # Use member attributes directly
        user_data["name"] = member.name
        user_data["descriminator"] = member.discriminator or "0000"  # Default if no discriminator

        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await interaction.response.send_message(file=file)

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx: commands.Context):
        """See the server leaderboard"""
        leaderboard_data = await get_leaderboard_data(self.bot, ctx.guild.id)

        embed = Embed(title="Leaderboard", description="")
        embed.set_thumbnail(url=os.environ.get("DISLEVEL_LEADERBOARD_ICON", ""))

        for position, data in enumerate(leaderboard_data, start=1):
            member = ctx.guild.get_member(data["member_id"]) if self.bot.intents.members else await ctx.guild.fetch_member(data["member_id"])
            if member:
                embed.description += f"{position}. {member.mention} - {data['xp']} XP\n"

        await ctx.send(embed=embed)

    @app_commands.command(name="leaderboard", description="See the server leaderboard (slash command)")
    async def leaderboard_slash(self, interaction: Interaction):
        """Slash command to view the server leaderboard"""
        leaderboard_data = await get_leaderboard_data(self.bot, interaction.guild.id)

        embed = Embed(title="Leaderboard", description="")
        embed.set_thumbnail(url=os.environ.get("DISLEVEL_LEADERBOARD_ICON", ""))

        for position, data in enumerate(leaderboard_data, start=1):
            member = interaction.guild.get_member(data["member_id"]) if self.bot.intents.members else await interaction.guild.fetch_member(data["member_id"])
            if member:
                embed.description += f"{position}. {member.mention} - {data['xp']} XP\n"

        await interaction.response.send_message(embed=embed)

    @commands.command()
    async def setbg(self, ctx: commands.Context, *, url: str):
        """Set background image of your card"""
        await set_bg_image(self.bot, ctx.author.id, ctx.guild.id, url)
        await ctx.send("Background image has been updated.")

    @commands.command()
    async def resetbg(self, ctx: commands.Context):
        """Reset background image of your card to default"""
        await set_bg_image(self.bot, ctx.author.id, ctx.guild.id, "")
        await ctx.send("Background image has been reset to default.")

    @app_commands.command(name="setbg", description="Set the background image of your card (slash command)")
    async def setbg_slash(self, interaction: Interaction, url: str):
        """Slash command to set background image of your card"""
        await set_bg_image(self.bot, interaction.user.id, interaction.guild.id, url)
        await interaction.response.send_message("Background image has been updated.")

    @app_commands.command(name="resetbg", description="Reset the background image of your card to default (slash command)")
    async def resetbg_slash(self, interaction: Interaction):
        """Slash command to reset background image of your card"""
        await set_bg_image(self.bot, interaction.user.id, interaction.guild.id, "")
        await interaction.response.send_message("Background image has been reset to default.")


async def setup(bot):
    await bot.add_cog(Leveling(bot))