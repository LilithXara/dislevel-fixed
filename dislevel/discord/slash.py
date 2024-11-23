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
    async def rank(self, interaction: Interaction, *, member: Optional[Member]):
        """Check rank of a user"""
        if not member:
            member = interaction.user

        user_data = await get_member_data(self.bot, member.id, interaction.guild.id)
        user_data["position"] = await get_member_position(
            self.bot, member.id, interaction.guild.id
        )
        user_data["profile_image"] = str(member.display_avatar.url)
        user_data["name"] = str(member).split("#")[0]
        user_data["descriminator"] = str(member).split("#")[1]

        image = await run_in_executor(get_card, data=user_data)
        file = File(fp=image, filename="card.png")

        await interaction.response.send_message(file=file)

    @app_commands.command(description="See the server leaderboard")
    async def leaderboard(self, interaction: Interaction):
        """See the server leaderboard"""
        print("DEBUG: Starting leaderboard command execution.")  # Debug start

        try:
            # Defer the interaction response to avoid timeout
            await interaction.response.defer()
            print("DEBUG: Deferred interaction response.")

            # Fetch leaderboard data
            leaderboard_data = await get_leaderboard_data(self.bot, interaction.guild.id)
            print(f"DEBUG: Retrieved leaderboard data: {leaderboard_data}")

            # Initialize the embed for the leaderboard
            embed = Embed(title="Leaderboard", description="")
            embed.set_thumbnail(url=os.environ.get("DISLEVEL_LEADERBOARD_ICON"))

            position = 0
            skipped_members = []  # Track skipped members for debugging

            for data in leaderboard_data:
                try:
                    print(f"DEBUG: Processing member ID {data['member_id']}")  # Log member processing
                    # Attempt to retrieve the member from cache or API
                    member = interaction.guild.get_member(data["member_id"])
                    if member is None:
                        print(f"DEBUG: Member ID {data['member_id']} not in cache, fetching from API.")
                        member = await interaction.guild.fetch_member(data["member_id"])

                    # Add member details to the embed
                    position += 1
                    embed.description += f"{position}. {member.mention} - {data['xp']} XP\n"
                    print(f"DEBUG: Successfully added member {member} to leaderboard.")  # Log success

                except discord.NotFound:
                    skipped_members.append(data['member_id'])
                    print(f"WARNING: Member ID {data['member_id']} not found. Skipping.")
                    continue
                except discord.Forbidden:
                    skipped_members.append(data['member_id'])
                    print(f"WARNING: Insufficient permissions to fetch member ID {data['member_id']}. Skipping.")
                    continue
                except discord.HTTPException as e:
                    skipped_members.append(data['member_id'])
                    print(f"WARNING: API error when fetching member {data['member_id']}: {e}")
                    continue
                except Exception as e:
                    skipped_members.append(data['member_id'])
                    print(f"ERROR: Unexpected error with member ID {data['member_id']}: {e}")
                    continue

            # Log skipped members for debugging
            print(f"DEBUG: Total skipped members: {len(skipped_members)}")
            print(f"DEBUG: Skipped member IDs: {skipped_members}")

            # Handle cases with no valid members
            if position == 0:
                embed.description = "No valid members found for leaderboard."
                print("DEBUG: No valid members found for leaderboard.")  # Log empty leaderboard

            print(f"DEBUG: Successfully generated leaderboard with {position} members.")
            await interaction.followup.send(embed=embed)  # Send a follow-up message

        except Exception as e:
            # Catch and log any issues in the main function
            print(f"ERROR: Unexpected error in leaderboard command: {e}")
            await interaction.followup.send(
                "An error occurred while retrieving the leaderboard. Please try again later.",
                ephemeral=True,
            )
        finally:
            print("DEBUG: Finished leaderboard command execution.")  # Debug end


async def setup(bot: commands.Bot):
    print("DEBUG: Loading LevelingSlash cog.")  # Debug log
    await bot.add_cog(LevelingSlash(bot))
    print("DEBUG: LevelingSlash cog loaded.")  # Debug log
