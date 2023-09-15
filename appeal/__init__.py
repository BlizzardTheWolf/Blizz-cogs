from .appealdm import AppealDM

def setup(bot):
    bot.add_cog(AppealDM(bot))
