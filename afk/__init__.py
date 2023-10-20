# Make sure you have this line in your __init__.py to register the cog when the bot starts
from .afk import AFK

async def setup(bot):
    await bot.add_cog(AFK(bot))
