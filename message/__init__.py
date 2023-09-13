from .mycog import MessageCog

async def setup(bot):
    bot.add_cog(MessageCog(bot))
