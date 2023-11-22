import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path
import os

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, to_mp3=False, max_size_mb=None):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo[ext=mp4]+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            conversion_message = await ctx.send(f"`Converting...`")  # Notify that the video is being converted

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

            file_size = renamed_file_path.stat().st_size  # Get file size in bytes

            if max_size_mb and file_size > max_size_mb * 1024 * 1024:
                await conversion_message.edit(content=f"`Converting... Done.\nTranscoding to required size...`")
                await self.transcode_video(renamed_file_path, max_size_mb)
                file_size = renamed_file_path.stat().st_size

            if file_size <= 8000000:  # Check if file size is less than or equal to 8 MB (Discord limit)
                await conversion_message.edit(content=f"`Converting... Done.\nUploading...`")
                # Send a new message with the converted file
                await ctx.send(f'`Here is the converted file:`',
                               file=discord.File(str(renamed_file_path)))
            else:
                # If the file size exceeds the limit, inform the user about the size
                await ctx.send(f"`The converted file is too large to send ({file_size / (1024 * 1024):.2f} MB). "
                               f"Discord has a file size limit of 8 MB for regular users. "
                               f"If you need to send larger files, consider boosting the server for a higher limit.`")
                # Remove the file after 10 minutes if it exists
                if renamed_file_path.exists():
                    renamed_file_path.unlink()

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"`An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

    async def transcode_video(self, input_file_path, max_size_mb):
        try:
            temp_output_path = input_file_path.parent / f"{input_file_path.stem}_temp{''.join(input_file_path.suffixes)}"

            # Use ffmpeg to transcode to a lower size
            ffmpeg_command = (
                f"ffmpeg -i {input_file_path} -b:v {max_size_mb}M -c:v libx264 -c:a aac -strict -2 {temp_output_path}"
            )
            os.system(ffmpeg_command)

            # Replace the original file with the transcoded one
            temp_output_path.replace(input_file_path)

        except Exception as e:
            error_message = str(e)
            print(f"Error during transcoding: {error_message}")

    @commands.command()
    async def ytmp3(self, ctx, url, max_size_mb=None):
        """
        Converts a YouTube video to MP3.

        Parameters:
        `<url>` The URL of the video you want to convert.
        `<max_size_mb>` (Optional) Maximum file size in MB.
        """
        await self.download_and_convert(ctx, url, to_mp3=True, max_size_mb=max_size_mb)

    @commands.command()
    async def ytmp4(self, ctx, url, max_size_mb=None):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<url>` The URL of the video you want to convert.
        `<max_size_mb>` (Optional) Maximum file size in MB.
        """
        await self.download_and_convert(ctx, url, to_mp3=False, max_size_mb=max_size_mb)
