from .appealdm import AppealDM

async def setup(bot):
    cog = AppealDM(bot)
    await bot.add_cog(cog)
