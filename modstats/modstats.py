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

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.log_action(guild, "bans")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.log_action(guild, "unbans")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log_action(member.guild, "kicks")

    @commands.Cog.listener()
    async def on_member_warn(self, member):
        await self.log_action(member.guild, "warns")

    async def get_action_counts(self, guild):
        action_counts = {
            "mutes_7_days": 0,
            "mutes_30_days": 0,
            "mutes_all_time": 0,
            "bans_7_days": 0,
            "bans_30_days": 0,
            "bans_all_time": 0,
            "kicks_7_days": 0,
            "kicks_30_days": 0,
            "kicks_all_time": 0,
            "warns_7_days": 0,
            "warns_30_days": 0,
            "warns_all_time": 0,
            "total_7_days": 0,
            "total_30_days": 0,
            "total_all_time": 0,
        }

        try:
            with open(os.path.join(self.data_dir, f"{guild.id}.json"), "r") as file:
                data = json.load(file)
                action_counts["mutes_7_days"] = data.get("mutes_7_days", 0)
                action_counts["mutes_30_days"] = data.get("mutes_30_days", 0)
                action_counts["mutes_all_time"] = data.get("mutes_all_time", 0)
                action_counts["bans_7_days"] = data.get("bans_7_days", 0)
                action_counts["bans_30_days"] = data.get("bans_30_days", 0)
                action_counts["bans_all_time"] = data.get("bans_all_time", 0)
                action_counts["kicks_7_days"] = data.get("kicks_7_days", 0)
                action_counts["kicks_30_days"] = data.get("kicks_30_days", 0)
                action_counts["kicks_all_time"] = data.get("kicks_all_time", 0)
                action_counts["warns_7_days"] = data.get("warns_7_days", 0)
                action_counts["warns_30_days"] = data.get("warns_30_days", 0)
                action_counts["warns_all_time"] = data.get("warns_all_time", 0)
                action_counts["total_7_days"] = (
                    data.get("mutes_7_days", 0)
                    + data.get("bans_7_days", 0)
                    + data.get("kicks_7_days", 0)
                    + data.get("warns_7_days", 0)
                )
                action_counts["total_30_days"] = (
                    data.get("mutes_30_days", 0)
                    + data.get("bans_30_days", 0)
                    + data.get("kicks_30_days", 0)
                    + data.get("warns_30_days", 0)
                )
                action_counts["total_all_time"] = (
                    data.get("mutes_all_time", 0)
                    + data.get("bans_all_time", 0)
                    + data.get("kicks_all_time", 0)
                    + data.get("warns_all_time", 0)
                )
        except FileNotFoundError:
            pass

        return action_counts

    @commands.command()
    async def modstats(self, ctx, user: discord.User = None):
        """Display moderation statistics for a user or the invoking user."""
        if user is None:
            user = ctx.author

        guild = ctx.guild
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        action_counts = await self.get_action_counts(guild)

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

def setup(bot):
    bot.add_cog(ModeratorStatsCog(bot))
