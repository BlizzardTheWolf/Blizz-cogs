from .changenametool import ChangeName

async def setup(bot):
    await bot.add_cog(ChangeName(bot))
