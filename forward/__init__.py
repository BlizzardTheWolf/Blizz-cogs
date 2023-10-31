from .forwarding import ForwardingCog

async def setup(bot):
    await bot.add_cog(ForwardingCog(bot))
