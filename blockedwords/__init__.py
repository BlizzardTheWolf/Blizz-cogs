from .blockedwords import BlockedWords

async def setup(bot):
    await bot.add_cog(BlockedWords(bot))
