from .joke import JokeCog

def setup(bot):
    bot.add_cog(JokeCog(bot))
