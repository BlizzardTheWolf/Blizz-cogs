import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, max_size_mb=8):
        try:
            output_folder = self.data_folder / "mp4"

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.mp4"),
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                    'max_filesize': max_size_mb * 1024 * 1024,  # Limit file size during conversion
                }],
            }

            conversion_message = await ctx.send(f"`Your video is being converted...`")

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    video_info = info_dict['entries'][0]
                else:
                    video_info = info_dict

                ydl.download([url])

            await asyncio.sleep(5)

            user = ctx.message.author
            downloaded_file_path = output_folder / f"{video_info['id']}.mp4"

            await conversion_message.edit(content=f"`Your video conversion to MP4 is complete. Uploading...`")
            await ctx.send(f'`Here is the converted file:`',
                           file=discord.File(str(downloaded_file_path)))

            # Remove the file after 10 minutes if it exists
            await asyncio.sleep(600)
            if downloaded_file_path.exists():
                downloaded_file_path.unlink()

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"`An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

    @commands.command()
    async def ytmp4(self, ctx, url, max_size_mb=8):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<url>` The URL of the video you want to convert.
        `[max_size_mb]` The maximum allowed file size in MB. Default is 8 MB.
        """
        await self.download_and_convert(ctx, url, max_size_mb=max_size_mb)
