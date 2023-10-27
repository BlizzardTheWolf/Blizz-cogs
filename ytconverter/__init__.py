from .converter import ConverterCog
from redbot.core.bot import Red

async def setup(bot: Red):
    await bot.add_cog(ConverterCog(bot))
