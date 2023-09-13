import discord
from redbot.core import commands, Config
from datetime import datetime, timedelta

class ModeratorStatsCog(commands.Cog):
    """Moderation statistics tracking."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change identifier

        default_guild_settings = {
            "mod_actions": []  # Store all moderation actions in a single list
        }

        self.config.register_guild(**default_guild_settings)

    @commands.command()
    @commands.guild_only()
    async def modstats(self, ctx, user: discord.User = None):
        """Display moderation statistics for a user."""
        if user is None:
            user = ctx.author

        guild = ctx.guild
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        mod_actions = await self.config.guild(guild).mod_actions()

        mod_actions_7_days = sum(1 for action in mod_actions if action["timestamp"] >= seven_days_ago)
        mod_actions_30_days = sum(1 for action in mod_actions if action["timestamp"] >= thirty_days_ago)
        mod_actions_all_time = len(mod_actions)

        embed = discord.Embed(title="Moderation Statistics", color=discord.Color.green())
        embed.add_field(name="Actions (last 7 days)", value=mod_actions_7_days, inline=True)
        embed.add_field(name="Actions (last 30 days)", value=mod_actions_30_days, inline=True)
        embed.add_field(name="Actions (all time)", value=mod_actions_all_time, inline=True)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.log_action(guild, "ban")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.log_action(guild, "unban")

    async def log_action(self, guild, action_type):
        timestamp = datetime.utcnow()
        action = {"timestamp": timestamp, "type": action_type}

        async with self.config.guild(guild).mod_actions() as mod_actions:
            mod_actions.append(action)

    async def cog_check(self, ctx):
        """Check if the user has mod or admin permissions."""
        return (
            ctx.author.guild_permissions.manage_messages
            or ctx.author.guild_permissions.ban_members
        )
