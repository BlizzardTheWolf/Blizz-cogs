import discord
from redbot.core import commands

class AwooCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx):
        """Send the setup message."""
        await ctx.send("I will now start setting up the bot in this server! You can check the commands with `;help`, more commands will be available after setup. Setting up the bot can take 10-30 minutes depending on size and current server load. **Make sure that this bot has full administrator permissions, or setup will fail!**")

def setup(bot):
    bot.add_cog(AwooCog(bot))
