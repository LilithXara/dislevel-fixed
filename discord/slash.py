import os
import discord
from typing import Optional, Union

from discord import Embed, File, Interaction, Member, app_commands
from discord.ext import commands
from easy_pil.utils import run_in_executor

from ..card import get_card
from ..utils import (
    get_leaderboard_data,
    get_member_data,
    get_member_position,
    set_bg_image,
)

# Confirm import works
print(f"DEBUG: Imported discord module: {discord.__name__}")


class LevelingSlash(commands.Cog):
    """Leveling commands"""

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        self.bot = bot

    @app_commands.command(description="Check rank of a user")
    @app_commands.allowed_installs(guilds=True, users=True)  # Allow both guild and user installations
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)  # Allow usage in all contexts
    async def rank(self, interaction: Interaction, member: Optional[Member] = None):
        """Check rank of a user"""
        member = member or interaction.user

        # Fetch user data
        user_data = await get_member_data(self.bot, member.id, interaction.guild.id)
        user_data["position"] = await get_member_position(self.bot, member.id, interaction.guild.id)
        user_data["profile_image"] = str(member.display_avatar.url)

        # Handle username and discriminator
        user_data["name"] = member.name
        user_data["descriminator"] = member.discriminator or "0000"  # Default if no discriminator

        # Generate the rank card
        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await interaction.response.send_message(file=file)

    @app_commands.command(description="See the server leaderboard")
    @app_commands.allowed_installs(guilds=True, users=True)  # Allow both guild and user installations
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)  # Allow usage in all contexts
    async def leaderboard(self, interaction: Interaction):
        """See the server leaderboard"""
        print("DEBUG: Starting leaderboard command execution.")

        try:
            await interaction.response.defer()
            print("DEBUG: Deferred interaction response.")

            leaderboard_data = await get_leaderboard_data(self.bot, interaction.guild.id)
            print(f"DEBUG: Retrieved leaderboard data: {leaderboard_data}")

            embed = Embed(title="Leaderboard", description="")
            embed.set_thumbnail(url=os.environ.get("DISLEVEL_LEADERBOARD_ICON", ""))

            position = 0
            skipped_members = []

            for data in leaderboard_data:
                try:
                    print(f"DEBUG: Processing member ID {data['member_id']}")
                    member = interaction.guild.get_member(data["member_id"]) or await interaction.guild.fetch_member(data["member_id"])

                    position += 1
                    embed.description += f"{position}. {member.mention} - {data['xp']} XP\n"
                    print(f"DEBUG: Successfully added member {member} to leaderboard.")

                except discord.NotFound:
                    skipped_members.append(data["member_id"])
                    print(f"WARNING: Member ID {data['member_id']} not found. Skipping.")
                except discord.Forbidden:
                    skipped_members.append(data["member_id"])
                    print(f"WARNING: Insufficient permissions to fetch member ID {data['member_id']}. Skipping.")
                except discord.HTTPException as e:
                    skipped_members.append(data["member_id"])
                    print(f"WARNING: API error when fetching member {data['member_id']}: {e}")
                except Exception as e:
                    skipped_members.append(data["member_id"])
                    print(f"ERROR: Unexpected error with member ID {data['member_id']}: {e}")

            print(f"DEBUG: Total skipped members: {len(skipped_members)}")
            print(f"DEBUG: Skipped member IDs: {skipped_members}")

            if position == 0:
                embed.description = "No valid members found for leaderboard."
                print("DEBUG: No valid members found for leaderboard.")

            print(f"DEBUG: Successfully generated leaderboard with {position} members.")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"ERROR: Unexpected error in leaderboard command: {e}")
            await interaction.followup.send(
                "An error occurred while retrieving the leaderboard. Please try again later.",
                ephemeral=True,
            )
        finally:
            print("DEBUG: Finished leaderboard command execution.")


async def setup(bot: commands.Bot):
    print("DEBUG: Loading LevelingSlash cog.")
    await bot.add_cog(LevelingSlash(bot))
    print("DEBUG: LevelingSlash cog loaded.")