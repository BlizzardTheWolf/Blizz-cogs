from .getemote import GetEmoteCog

async def setup(bot):
    await bot.add_cog(GetEmoteCog(bot))
