import discord
from redbot.core import commands, Config

class BlockedWords(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123456789)  # Use a different identifier
        self.config.register_global(message="You've used a blocked word. Please refrain from using it.")

    @commands.command()
    async def blockedwords(self, ctx):
        user = ctx.author
        message = await self.config.message()

        if not message:
            await ctx.send("Blocked words message is not set. Please configure it.")
            return

        try:
            await user.send(message)

    @commands.group()
    async def blockedwordsset(self, ctx):
        pass

    @blockedwordsset.command(name="message")
    async def blockedwordsset_message(self, ctx, *, message: str):
        await self.config.message.set(message)
        await ctx.send("Blocked words message has been updated.")

def setup(bot):
    bot.add_cog(BlockedWords(bot))
