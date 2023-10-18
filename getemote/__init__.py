from .getemote import GetEmote

async def setup(bot):
    await bot.add_cog(GetEmote(bot))
