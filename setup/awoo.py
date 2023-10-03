import discord
from redbot.core import commands

class AwooCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx):
        """Send the setup message."""
        await ctx.send("I will now start setting up the bot in this server! You can check the commands with `;help`. Setting up the bot can take 10-30 minutes depending on size and payload. ")

def setup(bot):
    bot.add_cog(AwooCog(bot))
