import discord
from redbot.core import Config, checks, commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123496789)
        default_global = {}
        self.config.register_global(**default_global)

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        blocked_guilds = await self.config.ign_servers()
        # Rest of your code

    @checks.is_owner()
    @commands.group()
    async def setautomodded(self, ctx):
        if not ctx.invoked_subcommand:
            pass

    @setautomodded.command(name="block")
    async def block(self, ctx, guild: discord.Guild):
        async with self.config.ign_servers() as blocked_guilds:
            if guild.id not in blocked_guilds:
                blocked_guilds.append(guild.id)

    @setautomodded.command(name="unblock")
    async def unblock(self, ctx, guild: discord.Guild):
        async with self.config.ign_servers() as blocked_guilds:
            if guild.id in blocked_guilds:
                blocked_guilds.remove(guild.id)

    async def _setup(self):
        if not hasattr(self.bot, "config"):
            raise RuntimeError("You need to run this on V3")

def setup(bot):
    bot.add_cog(AFK(bot))
