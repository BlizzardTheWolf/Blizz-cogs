import discord
from redbot.core import commands

class UwuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uwu(self, ctx, *, message: str):
        """OwO What's this?"""
        parts = message.split("::")
        uwu_message = ""

        for i, part in enumerate(parts):
            if i % 2 == 0:
                uwu_message += part.replace('l', 'w').replace('r', 'w').replace('L', 'W').replace('R', 'W')
            else:
                uwu_message += f"::{part}::"
        
        await ctx.send(uwu_message)

def setup(bot):
    bot.add_cog(UwuCog(bot))
