import discord
from redbot.core import commands, Config
from datetime import datetime, timedelta

class ModeratorStatsCog(commands.Cog):
    """Moderation statistics tracking."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier
        self.config.register_guild(
            mutes=[],
            bans=[],
            kicks=[],
            warns=[]
        )

    async def log_action(self, guild, action_type):
        timestamp = datetime.utcnow()
        async with self.config.guild(guild).get_attr(action_type) as actions:
            actions.append({"timestamp": timestamp})

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
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        mutes = await self.config.guild(guild).mutes()
        bans = await self.config.guild(guild).bans()
        kicks = await self.config.guild(guild).kicks()
        warns = await self.config.guild(guild).warns()

        mutes_7_days = sum(1 for mute in mutes if mute["timestamp"] >= seven_days_ago)
        mutes_30_days = sum(1 for mute in mutes if mute["timestamp"] >= thirty_days_ago)
        mutes_all_time = len(mutes)

        bans_7_days = sum(1 for ban in bans if ban["timestamp"] >= seven_days_ago)
        bans_30_days = sum(1 for ban in bans if ban["timestamp"] >= thirty_days_ago)
        bans_all_time = len(bans)

        kicks_7_days = sum(1 for kick in kicks if kick["timestamp"] >= seven_days_ago)
        kicks_30_days = sum(1 for kick in kicks if kick["timestamp"] >= thirty_days_ago)
        kicks_all_time = len(kicks)

        warns_7_days = sum(1 for warn in warns if warn["timestamp"] >= seven_days_ago)
        warns_30_days = sum(1 for warn in warns if warn["timestamp"] >= thirty_days_ago)
        warns_all_time = len(warns)

        total_7_days = mutes_7_days + bans_7_days + kicks_7_days + warns_7_days
        total_30_days = mutes_30_days + bans_30_days + kicks_30_days + warns_30_days
        total_all_time = mutes_all_time + bans_all_time + kicks_all_time + warns_all_time

        return {
            "mutes_7_days": mutes_7_days,
            "mutes_30_days": mutes_30_days,
            "mutes_all_time": mutes_all_time,
            "bans_7_days": bans_7_days,
            "bans_30_days": bans_30_days,
            "bans_all_time": bans_all_time,
            "kicks_7_days": kicks_7_days,
            "kicks_30_days": kicks_30_days,
            "kicks_all_time": kicks_all_time,
            "warns_7_days": warns_7_days,
            "warns_30_days": warns_30_days,
            "warns_all_time": warns_all_time,
            "total_7_days": total_7_days,
            "total_30_days": total_30_days,
            "total_all_time": total_all_time,
        }

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
