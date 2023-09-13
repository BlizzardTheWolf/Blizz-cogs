import discord
from redbot.core import commands, Config
from datetime import datetime, timedelta
import json
import os

class ModeratorStatsCog(commands.Cog):
    """Moderation statistics tracking."""

    def __init__(self, bot, command_prefix):
        self.bot = bot
        self.command_prefix = command_prefix  # Store the command prefix
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier

        default_guild_settings = {}

        self.config.register_guild(**default_guild_settings)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.User, *, reason: str):
        """Mute a user."""
        # Your mute logic here

        await self.log_action(ctx.guild, user.id, "mutes")

        await ctx.send(f"{user.mention} has been muted.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.User, *, reason: str):
        """Warn a user."""
        # Your warn logic here

        await self.log_action(ctx.guild, user.id, "warns")

        await ctx.send(f"{user.mention} has been warned.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason: str):
        """Ban a user."""
        # Your ban logic here

        await self.log_action(ctx.guild, user.id, "bans")

        await ctx.send(f"{user.mention} has been banned.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User, *, reason: str):
        """Kick a user."""
        # Your kick logic here

        await self.log_action(ctx.guild, user.id, "kicks")

        await ctx.send(f"{user.mention} has been kicked.")

    @commands.command()
    async def modstats(self, ctx, user: discord.User = None):
        """Display moderation statistics for a user or the invoking user."""
        if user is None:
            user = ctx.author

        guild = ctx.guild
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        action_counts = await self.get_action_counts(guild, user.id)

        embed = discord.Embed(title="Moderation Statistics", color=discord.Color.green())
        embed.add_field(name=f"Mutes (last 7 days)", value=action_counts["mutes_7_days"], inline=True)
        embed.add_field(name=f"Mutes (last 30 days)", value=action_counts["mutes_30_days"], inline=True)
        embed.add_field(name=f"Mutes (all time)", value=action_counts["mutes_all_time"], inline=True)
        embed.add_field(name=f"Bans (last 7 days)", value=action_counts["bans_7_days"], inline=True)
        embed.add_field(name=f"Bans (last 30 days)", value=action_counts["bans_30_days"], inline=True)
        embed.add_field(name=f"Bans (all time)", value=action_counts["bans_all_time"], inline=True)
        embed.add_field(name=f"Kicks (last 7 days)", value=action_counts["kicks_7_days"], inline=True)
        embed.add_field(name=f"Kicks (last 30 days)", value=action_counts["kicks_30_days"], inline=True)
        embed.add_field(name=f"Kicks (all time)", value=action_counts["kicks_all_time"], inline=True)
        embed.add_field(name=f"Warns (last 7 days)", value=action_counts["warns_7_days"], inline=True)
        embed.add_field(name=f"Warns (last 30 days)", value=action_counts["warns_30_days"], inline=True)
        embed.add_field(name=f"Warns (all time)", value=action_counts["warns_all_time"], inline=True)
        embed.add_field(name=f"Total (last 7 days)", value=action_counts["total_7_days"], inline=True)
        embed.add_field(name=f"Total (last 30 days)", value=action_counts["total_30_days"], inline=True)
        embed.add_field(name=f"Total (all time)", value=action_counts["total_all_time"], inline=True)

        await ctx.send(embed=embed)

    async def get_action_counts(self, guild, user_id):
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
            data_dir = os.path.join("/home/panda/.local/share/Red-DiscordBot/data/lake/moderatorstats", str(guild.id))
            data_file = os.path.join(data_dir, f"{user_id}.json")

            with open(data_file, "r") as file:
                data = json.load(file)
                action_counts["mutes_7_days"] = self.count_actions_in_duration(data["mutes"], seven_days_ago)
                action_counts["mutes_30_days"] = self.count_actions_in_duration(data["mutes"], thirty_days_ago)
                action_counts["mutes_all_time"] = len(data["mutes"])
                action_counts["bans_7_days"] = self.count_actions_in_duration(data["bans"], seven_days_ago)
                action_counts["bans_30_days"] = self.count_actions_in_duration(data["bans"], thirty_days_ago)
                action_counts["bans_all_time"] = len(data["bans"])
                action_counts["kicks_7_days"] = self.count_actions_in_duration(data["kicks"], seven_days_ago)
                action_counts["kicks_30_days"] = self.count_actions_in_duration(data["kicks"], thirty_days_ago)
                action_counts["kicks_all_time"] = len(data["kicks"])
                action_counts["warns_7_days"] = self.count_actions_in_duration(data["warns"], seven_days_ago)
                action_counts["warns_30_days"] = self.count_actions_in_duration(data["warns"], thirty_days_ago)
                action_counts["warns_all_time"] = len(data["warns"])
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
        except FileNotFoundError:
            pass

        return action_counts

    async def log_action(self, guild, user_id, action_type):
        timestamp = datetime.utcnow()

        data_dir = os.path.join("/home/panda/.local/share/Red-DiscordBot/data/lake/moderatorstats", str(guild.id))
        os.makedirs(data_dir, exist_ok=True)
        data_file = os.path.join(data_dir, f"{user_id}.json")

        try:
            with open(data_file, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        if action_type not in data:
            data[action_type] = []

        data[action_type].append(timestamp)

        with open(data_file, "w") as file:
            json.dump(data, file)

    def count_actions_in_duration(self, actions, duration):
        return sum(1 for action in actions if action >= duration)

def setup(bot):
    bot.add_cog(ModeratorStatsCog(bot, bot.command_prefix))  # Pass the command prefix
