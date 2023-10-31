from .forwardchannel import ForwardChannel

async def setup(bot):
    await bot.add_cog(ForwardChannel(bot))
