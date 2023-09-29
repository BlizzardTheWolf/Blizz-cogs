from .randomresponse import RandomResponse

async def setup(bot):
    await bot.add_cog(RandomResponse(bot))
