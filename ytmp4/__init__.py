from .converter import YTMP4Cog

async def setup(bot):
    await bot.add_cog(YTMP4Cog(bot))
