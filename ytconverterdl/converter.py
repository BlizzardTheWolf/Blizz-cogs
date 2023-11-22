import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path
from moviepy.editor import VideoFileClip

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def resize_video(self, input_path, output_path):
        try:
            # Load the video clip
            video_clip = VideoFileClip(str(input_path))

            # Resize the video to 720p
            resized_clip = video_clip.resize(height=720)

            # Write the resized video to the output path
            resized_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, threads=4)

        except Exception as e:
            raise ValueError(f"Error during video resizing: {e}")

    async def download_and_convert(self, ctx, url, to_mp3=False):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best' if not to_mp3 else 'bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            conversion_message = await ctx.send(f"`Downloading...`")

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

            await conversion_message.edit(content=f"`Transcoding to 720p...`")
            # Resize the video to 720p
            await self.resize_video(renamed_file_path, renamed_file_path)

            await conversion_message.edit(content=f"`Uploading...`")
            # Send a new message with the converted file
            await ctx.send(f'`Done`', file=discord.File(str(renamed_file_path)))

            # Remove the file after 1 minute if it exists
            await asyncio.sleep(60)
            if renamed_file_path.exists():
                renamed_file_path.unlink()

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"`An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

    @commands.command()
    async def ytmp3(self, ctx, url):
        """
        Converts a YouTube video to MP3.

        Parameters:
        `<url>` The URL of the video you want to convert.
        """
        await self.download_and_convert(ctx, url, to_mp3=True)

    @commands.command()
    async def ytmp4(self, ctx, url):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<url>` The URL of the video you want to convert.
        """
        await self.download_and_convert(ctx, url, to_mp3=False)
