from .unmute_hide import UnmuteHideCog

def setup(bot):
    await bot.add_cog(UnmuteHideCog(bot))
