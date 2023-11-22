import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path
from moviepy.editor import VideoFileClip, sys

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def resize_video(self, input_path, output_path, target_size_bytes):
        try:
            # Load the video clip
            video_clip = VideoFileClip(str(input_path))

            # Calculate the audio bitrate
            audio_bitrate = video_clip.audio.bitrate * 1024

            # Calculate the video duration in bytes
            video_duration_bytes = video_clip.duration * audio_bitrate

            # Calculate the target bitrate
            target_bitrate = target_size_bytes * 8 / video_duration_bytes

            # Resize the video and adjust the bitrate
            resized_clip = video_clip.resize(height=720)
            resized_clip = resized_clip.set_audio(resized_clip.audio.set_bitrate(str(target_bitrate) + 'bit'))

            # Write the resized video to the output path
            resized_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, threads=4)

        except Exception as e:
            raise ValueError(f"Error during video resizing: {e}")

    async def download_and_convert(self, ctx, url, to_mp3=False, max_size_mb=None):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo[ext=mp4]+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            conversion_message = await ctx.send(f"`Converting...`")

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

            file_size = renamed_file_path.stat().st_size

            if max_size_mb is not None and file_size > max_size_mb * 1024 * 1024:
                await conversion_message.edit(content=f"`Transcoding to your specified size...`")
                # Resize the video to meet the size requirement
                await self.resize_video(renamed_file_path, renamed_file_path, max_size_mb * 1024 * 1024)

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
    async def ytmp
