from .appealdm import AppealDM

def setup(bot):
    cog = AppealDM(bot)
    bot.add_cog(cog)
