from .tod import TruthOrDare

def setup(bot):
    await bot.add_cog(TruthOrDare(bot))
