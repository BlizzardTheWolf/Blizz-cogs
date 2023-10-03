import discord
from redbot.core import commands

class AwooCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx):
        """Send the setup message."""
        await ctx.send("Awooooooo!")

def setup(bot):
    bot.add_cog(AwooCog(bot))
