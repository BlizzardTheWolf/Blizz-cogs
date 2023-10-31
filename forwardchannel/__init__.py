from .forwardchannel import ForwardChannel

async def setup(bot):
    cog = ForwardChannel(bot)
    await bot.add_cog(cog)
    await bot.add_listener(cog.forward_message, "on_message")
