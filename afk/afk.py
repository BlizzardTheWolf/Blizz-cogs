import discord
from redbot.core import commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_statuses = {}  # Dictionary to store AFK statuses

    @commands.command()
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Set your AFK status with an optional reason."""
        self.afk_statuses[ctx.author.id] = reason
        await ctx.send(f"{ctx.author.mention} is now AFK: {reason}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.afk_statuses:
            del self.afk_statuses[message.author.id]  # Clear AFK status upon sending a message

def setup(bot):
    afk_cog = AFK(bot)
    bot.add_cog(afk_cog)
