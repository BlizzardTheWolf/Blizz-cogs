from .message import MessageCog

async def setup(bot):
    cog = MessageCog(bot)
    bot.add_cog(cog)
