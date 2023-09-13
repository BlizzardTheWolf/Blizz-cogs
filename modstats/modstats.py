import discord
from redbot.core import commands, Config
from datetime import datetime, timedelta

class ModeratorStatsCog(commands.Cog):
    """Moderation statistics tracking."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier

        default_guild_settings = {}

        self.config.register_guild(**default_guild_settings)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.User, *, reason: str):
        """Mute a user."""
        # Your mute logic here

        await self.log_action(ctx.guild, "mutes")

        await ctx.send(f"{user.mention} has been muted.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.User, *, reason: str):
        """Warn a user."""
        # Your warn logic here

        await self.log_action(ctx.guild, "warns")

        await ctx.send(f"{user.mention} has been warned.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason: str):
        """Ban a user."""
        # Your ban logic here

        await self.log_action(ctx.guild, "bans")

        await ctx.send(f"{user.mention} has been banned.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User, *, reason: str):
        """Kick a user."""
        # Your kick logic here

        await self.log_action(ctx.guild, "kicks")

        await ctx.send(f"{user.mention} has been kicked.")

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
            action_data = await self.config.guild(guild).get_raw("action_data")
            action_counts["mutes_7_days"] = action_data.get("mutes_7_days", 0)
            action_counts["mutes_30_days"] = action_data.get("mutes_30_days", 0)
            action_counts["mutes_all_time"] = action_data.get("mutes_all_time", 0)
            action_counts["bans_7_days"] = action_data.get("bans_7_days", 0)
            action_counts["bans_30_days"] = action_data.get("bans_30_days", 0)
            action_counts["bans_all_time"] = action_data.get("bans_all_time", 0)
            action_counts["kicks_7_days"] = action_data.get("kicks_7_days", 0)
            action_counts["kicks_30_days"] = action_data.get("kicks_30_days", 0)
            action_counts["kicks_all_time"] = action_data.get("kicks_all_time", 0)
            action_counts["warns_7_days"] = action_data.get("warns_7_days", 0)
            action_counts["warns_30_days"] = action_data.get("warns_30_days", 0)
            action_counts["warns_all_time"] = action_data.get("warns_all_time", 0)
            action_counts["total_7_days"] = (
                action_counts["mutes_7_days"] + action_counts["bans_7_days"]
                + action_counts["kicks_7_days"] + action_counts["warns_7_days"]
            )
            action_counts["total_30_days"] = (
                action_counts["mutes_30_days"] + action_counts["bans_30_days"]
                + action_counts["kicks_30_days"] + action_counts["warns_30_days"]
            )
            action_counts["total_all_time"] = (
                action_counts["mutes_all_time"] + action_counts["bans_all_time"]
                + action_counts["kicks_all_time"] + action_counts["warns_all_time"]
            )
        except KeyError:
            pass

        return action_counts

    async def log_action(self, guild, action_type):
        timestamp = datetime.utcnow()
        action_data = await self.config.guild(guild).action_data()

        if action_type not in action_data:
            action_data[action_type] = []

        action_data[action_type].append(timestamp)
        await self.config.guild(guild).action_data.set(action_data)
