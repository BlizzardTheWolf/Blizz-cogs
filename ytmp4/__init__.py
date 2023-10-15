from .yt_to_mp4 import YTtoMP4

def setup(bot):
    bot.add_cog(YTtoMP4(bot))
