from .multicommand import MultiCommand

async def setup(bot):
    await bot.add_cog(MultiCommand(bot))
