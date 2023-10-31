from .forwardchannel import ForwardChannel

async def setup(bot):
    cog = ForwardChannel(bot)
    await bot.add_cog(cog)
