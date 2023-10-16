from .ytmp3 import YTMP3Cog

async def setup(bot):
    await bot.add_cog(YTMP3Cog(bot))
