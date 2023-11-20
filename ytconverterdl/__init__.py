from .converter import ConverterCog

async def setup(bot):
    await bot.add_cog(ConverterCog(bot))
