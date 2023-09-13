from .message import MessageCog

async def setup(bot):
    cog = MessageCog(bot)
    await bot.add_cog(cog)
