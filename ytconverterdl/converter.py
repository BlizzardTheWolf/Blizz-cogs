import discord
from redbot.core import commands
import youtube_dlp
import asyncio
import time
from redbot.core import data_manager

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, to_mp3=False):
        try:
            ydl_opts = {
                'format': 'bestaudio' if to_mp3 else 'bestvideo+bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4' if not to_mp3 else 'mp3',
                }],
                'outtmpl': str(self.data_folder / "downloads" / f'%(title)s.%(ext)s'),
                'verbose': True,
            }

            with youtube_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                if 'entries' in info_dict:
                    video = info_dict['entries'][0]
                else:
                    video = info_dict

                if video.get('age_limit', 0) > 0:
                    await ctx.send("This video is age-restricted and cannot be converted.")
                    return

                duration = video.get('duration', 0)

                if duration > 900:
                    await ctx.send("Video exceeds the maximum time limit of 15 minutes.")
                    return

                await ctx.send(f"Converting the video, please wait...")

                # Rest of your code remains unchanged...

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}")

    @commands.command()
    async def ytmp3(self, ctx, url):
        """
        Converts a YouTube video to MP3.
        Parameters:
        `<url>` The url of the video you want to convert.
        """
        await self.download_and_convert(ctx, url, to_mp3=True)

    @commands.command()
    async def ytmp4(self, ctx, url):
        """
        Converts a YouTube video to MP4.
        **Parameters:**
        `<url>` The url of the video you want to convert.
        """
        await self.download_and_convert(ctx, url, to_mp3=False)

def setup(bot):
    bot.add_cog(ConverterCog(bot))
