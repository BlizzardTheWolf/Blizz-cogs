from .ytmp4 import YTMP4Cog

async def setup(bot):
    cog = YTMP4Cog(bot)
    await bot.add_cog(cog)
