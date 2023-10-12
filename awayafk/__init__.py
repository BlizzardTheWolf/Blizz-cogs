from .afk import AFKCog

async def setup(bot):
    cog = AFKCog(bot)
    await bot.add_cog(cog)
