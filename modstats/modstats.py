import discord
from redbot.core import commands
from datetime import datetime, timedelta
import os
import json

class ModeratorStatsCog(commands.Cog):
    """Moderation statistics tracking."""

    def __init__(self, bot):
        self.bot = bot
        self.data_dir = "/home/panda/.local/share/Red-DiscordBot/data/lake/modstats"

    async def log_action(self, guild, action_type):
        timestamp = datetime.utcnow()
        data_file = os.path.join(self.data_dir, f"{guild.id}.json")

        try:
            with open(data_file, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        if action_type not in data:
            data[action_type] = []

        data[action_type].append({"timestamp": timestamp})

        with open(data_file, "w") as file:
            json.dump(data, file, indent=4)

    async def on_member_ban(self, guild, user):
        await self.log_action(guild, "bans")

    async def on_member_unban(self, guild, user):
        await self.log_action(guild, "unbans")

    async def on_member_remove(self, member):
        await self.log_action(member.guild, "kicks")

    async def on_member_warn(self, member):
        await self.log_action(member.guild, "warns")

    async def get_action_counts(self, guild):
        # The same get_action_counts code as before

    @commands.command()
    async def modstats(self, ctx, user: discord.User = None):
        """Display moderation statistics for a user or the invoking user."""
        # The same modstats code as before

def setup(bot):
    bot.add_cog(ModeratorStatsCog(bot))
