from .joke import JokeCog

async def setup(bot):
    await bot.add_cog(JokeCog(bot))
