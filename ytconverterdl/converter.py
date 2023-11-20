import discord
from redbot.core import commands
import youtube_dl
import asyncio
time
import os
from redbot.core import data_manager
import shutil

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
                'verbose': True,  # Add this line to enable verbose output
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info_dict)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to {"mp3" if to_mp3 else "mp4"} is complete. Here is the converted file:',
                           file=discord.File(video_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(video_path)

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
