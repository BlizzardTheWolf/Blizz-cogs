from .unmute_hide import UnmuteHideCog

async def setup(bot):
    await bot.add_cog(UnmuteHideCog(bot))
