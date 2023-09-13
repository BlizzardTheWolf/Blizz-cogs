from .modstats import ModeratorStatsCog

async def setup(bot):
    await bot.add_cog(ModeratorStatsCog(bot))
