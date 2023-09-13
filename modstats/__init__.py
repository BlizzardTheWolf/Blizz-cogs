from .modstats import ModeratorStatsCog

def setup(bot):
    bot.add_cog(ModeratorStatsCog(bot))
