from .modstats import ModeratorStatsCog

async def setup(bot):
    bot.add_cog(ModeratorStatsCog(bot))
