from .automodded import AutoModCog

async def setup(bot):
    await bot.add_cog(AutoModCog(bot))
