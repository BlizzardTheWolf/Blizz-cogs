from .cleanupguild import CleanupGuild

async def setup(bot):
    await bot.add_cog(CleanupGuild(bot))
