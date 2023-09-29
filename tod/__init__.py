from .tod import TruthOrDare

async def setup(bot):
    cog = TruthOrDare(bot)
    await bot.add_cog(cog)
