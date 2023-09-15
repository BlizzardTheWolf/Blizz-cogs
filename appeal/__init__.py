from .appealdm import AppealDM

async def setup(bot):
    cog = AppealDM(bot)
    await cog.initialize()
    bot.add_cog(cog)
