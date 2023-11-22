import discord
from redbot.core import commands
import asyncio
from redbot.core import data_manager
from pathlib import Path
import subprocess

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
            }

            conversion_message = await ctx.send(f"`Your video is being converted...`")

            with subprocess.Popen(
                [
                    "youtube-dl",
                    "--format",
                    f"bestvideo[filesize<{max_size_mb}M]+bestaudio/best",
                    "--output",
                    str(output_folder / "%(id)s.mp4"),
                    "--",
                    url,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ) as process:
                _, error_output = process.communicate()

                if process.returncode != 0:
                    raise Exception(error_output)

            await asyncio.sleep(5)

            user = ctx.message.author
            downloaded_file_path = output_folder / f"{ydl_opts['outtmpl']}"
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
        Converts a YouTube video to MP4 with a maximum allowed file size.

        Parameters:
        `<url>` The URL of the video you want to convert.
        `[max_size_mb]` The maximum allowed file size in MB. Default is 8 MB.
        """
        await self.download_and_convert(ctx, url, max_size_mb=max_size_mb)
