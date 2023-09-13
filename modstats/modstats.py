import discord
from redbot.core import commands, Config
from datetime import datetime, timedelta
import os  # Import the os module
import json  # Import the json module

class ModeratorStatsCog(commands.Cog):
    """Moderation statistics tracking."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier

        # Define the directory path for storing JSON files
        self.data_dir = "/home/panda/.local/share/Red-DiscordBot/data/lake/modstats"

        default_guild_settings = {
            "mutes": [],
            "bans": [],
            "kicks": [],
            "warns": []
        }

        self.config.register_guild(**default_guild_settings)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def modstats(self, ctx, user: discord.User = None):
        """Display moderation statistics for a user."""
        if user is None:
            user = ctx.author

        guild = ctx.guild
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        mutes = await self.load_actions(guild, "mutes")
        bans = await self.load_actions(guild, "bans")
        kicks = await self.load_actions(guild, "kicks")
        warns = await self.load_actions(guild, "warns")

        action_counts = {
            "mutes_7_days": sum(1 for mute in mutes if mute["timestamp"] >= seven_days_ago),
            "mutes_30_days": sum(1 for mute in mutes if mute["timestamp"] >= thirty_days_ago),
            "mutes_all_time": len(mutes),
            "bans_7_days": sum(1 for ban in bans if ban["timestamp"] >= seven_days_ago),
            "bans_30_days": sum(1 for ban in bans if ban["timestamp"] >= thirty_days_ago),
            "bans_all_time": len(bans),
            "kicks_7_days": sum(1 for kick in kicks if kick["timestamp"] >= seven_days_ago),
            "kicks_30_days": sum(1 for kick in kicks if kick["timestamp"] >= thirty_days_ago),
            "kicks_all_time": len(kicks),
            "warns_7_days": sum(1 for warn in warns if warn["timestamp"] >= seven_days_ago),
            "warns_30_days": sum(1 for warn in warns if warn["timestamp"] >= thirty_days_ago),
            "warns_all_time": len(warns),
            "total_7_days": 0,
            "total_30_days": 0,
            "total_all_time": 0
        }

        action_counts["total_7_days"] = (
            action_counts["mutes_7_days"]
            + action_counts["bans_7_days"]
            + action_counts["kicks_7_days"]
            + action_counts["warns_7_days"]
        )

        action_counts["total_30_days"] = (
            action_counts["mutes_30_days"]
            + action_counts["bans_30_days"]
            + action_counts["kicks_30_days"]
            + action_counts["warns_30_days"]
        )

        action_counts["total_all_time"] = (
            action_counts["mutes_all_time"]
            + action_counts["bans_all_time"]
            + action_counts["kicks_all_time"]
            + action_counts["warns_all_time"]
        )

        embed = discord.Embed(title="Moderation Statistics", color=discord.Color.green())
        embed.add_field(name="Mutes (last 7 days)", value=action_counts["mutes_7_days"], inline=True)
        embed.add_field(name="Mutes (last 30 days)", value=action_counts["mutes_30_days"], inline=True)
        embed.add_field(name="Mutes (all time)", value=action_counts["mutes_all_time"], inline=True)
        embed.add_field(name="Bans (last 7 days)", value=action_counts["bans_7_days"], inline=True)
        embed.add_field(name="Bans (last 30 days)", value=action_counts["bans_30_days"], inline=True)
        embed.add_field(name="Bans (all time)", value=action_counts["bans_all_time"], inline=True)
        embed.add_field(name="Kicks (last 7 days)", value=action_counts["kicks_7_days"], inline=True)
        embed.add_field(name="Kicks (last 30 days)", value=action_counts["kicks_30_days"], inline=True)
        embed.add_field(name="Kicks (all time)", value=action_counts["kicks_all_time"], inline=True)
        embed.add_field(name="Warns (last 7 days)", value=action_counts["warns_7_days"], inline=True)
        embed.add_field(name="Warns (last 30 days)", value=action_counts["warns_30_days"], inline=True)
        embed.add_field(name="Warns (all time)", value=action_counts["warns_all_time"], inline=True)
        embed.add_field(name="Total (last 7 days)", value=action_counts["total_7_days"], inline=True)
        embed.add_field(name="Total (last 30 days)", value=action_counts["total_30_days"], inline=True)
        embed.add_field(name="Total (all time)", value=action_counts["total_all_time"], inline=True)

        await ctx.send(embed=embed)

    async def load_actions(self, guild, action_type):
        # Define the path for the JSON file for the guild's actions
        guild_dir = os.path.join(self.data_dir, str(guild.id))
        action_file = os.path.join(guild_dir, f"{action_type}.json")

        # Create the guild directory if it doesn't exist
        os.makedirs(guild_dir, exist_ok=True)

        # Load the JSON file or create an empty list if it doesn't exist
        if os.path.exists(action_file):
            with open(action_file, "r") as file:
                return json.load(file)
        else:
            return []

    async def save_actions(self, guild, action_type, actions):
        # Define the path for the JSON file for the guild's actions
        guild_dir = os.path.join(self.data_dir, str(guild.id))
        action_file = os.path.join(guild_dir, f"{action_type}.json")

        # Create the guild directory if it doesn't exist
        os.makedirs(guild_dir, exist_ok=True)

        # Save the actions to the JSON file
        with open(action_file, "w") as file:
            json.dump(actions, file)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.log_action(guild, "bans")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.log_action(guild, "unbans")

    async def log_action(self, guild, action_type):
        timestamp = datetime.utcnow()
        action = {"timestamp": timestamp, "type": action_type}

        if action_type == "bans":
            async with self.config.guild(guild).bans() as bans:
                bans.append(action)
        elif action_type == "unbans":
            async with self.config.guild(guild).bans() as bans:
                # Remove the corresponding ban action based on your implementation
                pass  # Add your logic here

        # Implement similar logic for mutes, kicks, and warns

def setup(bot):
    bot.add_cog(ModeratorStatsCog(bot))
