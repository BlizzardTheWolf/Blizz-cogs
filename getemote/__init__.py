from .getemote import GetEmoteCog

def setup(bot):
    bot.add_cog(GetEmoteCog(bot))
