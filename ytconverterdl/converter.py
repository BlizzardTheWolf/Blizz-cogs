import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path
import subprocess

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, to_mp3=False, max_size_mb=None):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            conversion_message = await ctx.send(f"`Converting video...`")

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    video_info = info_dict['entries'][0]
                else:
                    video_info = info_dict

                ydl.download([url])

            await asyncio.sleep(5)

            user = ctx.message.author
            downloaded_file_path = output_folder / f"{video_info['id']}.{'mp3' if to_mp3 else 'webm'}"
            renamed_file_path = output_folder / f"{video_info['id']}.{'mp3' if to_mp3 else 'mp4'}"

            downloaded_file_path.rename(renamed_file_path)

            # Check if the file size exceeds the limit
            file_size = renamed_file_path.stat().st_size  # Get file size in bytes
            if max_size_mb and file_size > max_size_mb * 1024 * 1024:
                await conversion_message.edit(content=f"`Transcoding video to required size...`")
                transcoded_file_path = output_folder / f"{video_info['id']}_transcoded.{'mp3' if to_mp3 else 'mp4'}"
                target_size = max_size_mb * 1024 * 1024 - 100000  # 100 KB buffer
                subprocess.run(['ffmpeg', '-i', str(renamed_file_path), '-b', '1000k', '-fs', str(target_size), str(transcoded_file_path)])
                renamed_file_path.unlink()
                renamed_file_path = transcoded_file_path

            # Try uploading the file
            try:
                await conversion_message.edit(content=f"`Uploading video...`")
                # Send a new message with the converted file, mentioning the user
                await ctx.send(f'{user.mention}, `Here is the converted video:`',
                               file=discord.File(str(renamed_file_path)))
                await conversion_message.edit(content=f"`Video uploaded successfully.`")
            except discord.errors.HTTPException as upload_error:
                # If uploading fails, send an error message
                await ctx.send(f"`An error occurred during upload. Please check the file and try again.\nError details: {upload_error}`")

            # Remove the file after 1 minute if it exists
            await asyncio.sleep(60)
            if renamed_file_path.exists():
                renamed_file_path.unlink()

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"`An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

    @commands.command()
    async def ytmp3(self, ctx, url, max_size_mb=None):
        """
        Converts a YouTube video to MP3.

        Parameters:
        `<url>` The URL of the video you want to convert.
        `[max_size_mb]` (Optional) The maximum size of the converted file in megabytes.
        """
        await self.download_and_convert(ctx, url, to_mp3=True, max_size_mb=max_size_mb)

    @commands.command()
    async def ytmp4(self, ctx, url, max_size_mb=None):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<url>` The URL of the video you want to convert.
        `[max_size_mb]` (Optional) The maximum size of the converted file in megabytes.
        """
        await self.download_and_convert(ctx, url, to_mp3=False, max_size_mb=max_size_mb)
