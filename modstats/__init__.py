from .modstats import ModeratorStatsCog

async def setup(bot):
    bot.add_cog(ModeratorStatsCog(bot, bot.command_prefix))  # Pass the command prefix
