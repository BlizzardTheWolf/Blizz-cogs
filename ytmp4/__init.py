from .youtubetomp4 import YouTubeToMP4Cog

def setup(bot):
    cog = YouTubeToMP4Cog(bot)
    bot.add_cog(cog)
