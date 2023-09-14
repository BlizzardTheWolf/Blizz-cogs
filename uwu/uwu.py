import discord
from redbot.core import commands

class UwuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uwu(self, ctx, *, message: str):
        """UwU-nize any message! OwO"""
        message = message.replace('l', 'w').replace('r', 'w').replace('L', 'W').replace('R', 'W')
        await ctx.send(message)

def setup(bot):
    bot.add_cog(UwuCog(bot))
