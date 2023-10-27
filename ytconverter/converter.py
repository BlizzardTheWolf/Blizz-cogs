import discord
from redbot.core import commands
import asyncio
import time
import os
from redbot.core import data_manager

from moviepy.editor import *

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(self)

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            video = VideoFileClip(url)
            
            if video is None:
                await ctx.send("Could not find the video for conversion.")
                return

            await ctx.send("Converting the video to MP3, please wait...")

            # Get the video code from the YouTube URL
            video_code = str(int(time.time())) + ".mp3"
            audio_path = self.data_folder / video_code

            audio = video.audio
            audio.write_audiofile(str(audio_path))

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to MP3 is complete. Here is the converted audio:', file=discord.File(str(audio_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(str(audio_path))

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

    @commands.command()
    async def ytmp4(self, ctx, url):
        try:
            video = VideoFileClip(url)
            
            if video is None:
                await ctx.send("Could not find the video for conversion.")
                return

            await ctx.send("Converting the video to mp4, please wait...")

            # Generate a unique filename with timestamp
            video_code = str(int(time.time())) + ".mp4"
            video_path = self.data_folder / video_code

            video.write_videofile(str(video_path))

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to mp4 is complete. Here is the converted video:', file=discord.File(str(video_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(str(video_path))

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(ConverterCog(bot))
