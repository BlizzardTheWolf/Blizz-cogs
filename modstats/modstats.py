import discord
from redbot.core import commands
from datetime import datetime, timedelta
import os
import json

class DataHandler:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load_data(self, guild):
        data_file = os.path.join(self.data_dir, f"{guild.id}.json")
        try:
            with open(data_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_data(self, guild, data):
        data_file = os.path.join(self.data_dir, f"{guild.id}.json")
        with open(data_file, "w") as file:
            json.dump(data, file, indent=4)

class ModeratorStatsCog(commands.Cog):
    """Moderation statistics tracking."""

    def __init__(self, bot):
        self.bot = bot
        self.data_handler = DataHandler("/home/panda/.local/share/Red-DiscordBot/data/lake/modstats")

    async def log_action(self, guild, action_type):
        timestamp = datetime.utcnow()
        data = self.data_handler.load_data(guild)

        if action_type not in data:
            data[action_type] = []

        data[action_type].append({"timestamp": timestamp})

        self.data_handler.save_data(guild, data)

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
        data = self.data_handler.load_data(guild)
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

        for action_type, actions in data.items():
            for action in actions:
                if action["timestamp"] >= datetime.utcnow() - timedelta(days=7):
                    action_counts[f"{action_type}_7_days"] += 1
                if action["timestamp"] >= datetime.utcnow() - timedelta(days=30):
                    action_counts[f"{action_type}_30_days"] += 1
                action_counts[f"{action_type}_all_time"] += 1

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

        return action_counts

    @commands.command()
    async def modstats(self, ctx, user: discord.User = None):
        """Display moderation statistics for a user or the invoking user."""
        if user is None:
            user = ctx.author

        guild = ctx.guild
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
