from .awoo import AwooCog

async def setup(bot):
    await bot.add_cog(AwooCog(bot))
