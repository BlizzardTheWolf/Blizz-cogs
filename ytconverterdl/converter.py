import discord
from redbot.core import commands
import asyncio
from redbot.core import data_manager
from pathlib import Path
import os

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, max_size_mb=8):
        try:
            output_folder = self.data_folder / "mp4"

            # Calculate max video bitrate based on max file size
            max_video_bitrate = int((max_size_mb * 1024 * 8) / 10)  # 10 seconds duration for simplicity

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.mp4"),
                'postprocessors': [
                    {
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                        'parameters': [
                            '-b:v', f'{max_video_bitrate}k',
                            '-maxrate', f'{max_video_bitrate}k',
                            '-bufsize', f'{2 * max_video_bitrate}k',
                        ],
                    },
                ],
            }

            conversion_message = await ctx.send(f"`Your video is being converted...`")

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    video_info = info_dict['entries'][0]
                else:
                    video_info = info_dict

                ydl.download([url])

            await asyncio.sleep(5)

            user = ctx.message.author
            downloaded_file_path = output_folder / f"{ydl_opts['outtmpl']}"
            await conversion_message.edit(content=f"`Your video conversion to MP4 is complete. Uploading...`")

            file_size_mb = os.path.getsize(downloaded_file_path) / (1024 ** 2)
            if file_size_mb > max_size_mb:
                raise ValueError(f"File size exceeds the allowed limit of {max_size_mb} MB.")

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
        Converts a YouTube video to MP4 with a maximum allowed file size.

        Parameters:
        `<url>` The URL of the video you want to convert.
        `[max_size_mb]` The maximum allowed file size in MB. Default is 8 MB.
        """
        try:
            await self.download_and_convert(ctx, url, max_size_mb=max_size_mb)
        except ValueError as ve:
            await ctx.send(f"`Error: {ve}`")
