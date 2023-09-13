from .modstats import ModeratorStatsCog

def setup(bot):
    await bot.add_cog(ModeratorStatsCog(bot))
