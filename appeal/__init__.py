from .appealdm import AppealDM

async def setup(bot):
    await bot.add_cog(AppealDM(bot))
