from .yt_to_mp4 import YTtoMP4

async def setup(bot):
    await bot.add_cog(YTtoMP4(bot))
