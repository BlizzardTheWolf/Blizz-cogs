from .youtubetomp4 import YouTubeToMP4Cog

async def setup(bot):
    cog = YouTubeToMP4Cog(bot)
    await bot.add_cog(cog)
