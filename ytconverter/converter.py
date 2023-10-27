import discord
from redbot.core import commands, data_manager
from pytube import YouTube
import asyncio
import time
import os

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(self)

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            stream = yt.streams.filter(only_audio=True).first()

            if not stream:
                await ctx.send("Could not find an audio stream for download.")
                return

            await ctx.send("Converting the video to MP3, please wait...")

            # Get the video code from the YouTube URL
            video_code = yt.video_id

            audio_path = self.data_folder / f'{video_code}.mp3'

            # Download the audio without an extension
            stream.download(output_path=str(self.data_folder), filename=video_code)

            # Rename the file with .mp3 extension
            audio_path.rename(f'{audio_path}.mp3')

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to MP3 is complete. Here is the converted audio:',
                           file=discord.File(str(audio_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(str(audio_path))

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

    @commands.command()
    async def ytmp4(self, ctx, url):
        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()

            if not stream:
                await ctx.send("Could not find a suitable mp4 stream for download.")
                return

            duration = yt.length

            if duration > 900:
                await ctx.send("Video exceeds the maximum time limit of 15 minutes.")
                return

            await ctx.send("Converting the video to mp4, please wait...")

            # Generate a unique filename with timestamp
            video_code = str(int(time.time())) + ".mp4"
            video_path = self.data_folder / video_code

            # Download the video
            stream.download(output_path=str(self.data_folder), filename=video_code)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to mp4 is complete. Here is the converted video:',
                           file=discord.File(str(video_path))

            # Remove the file after 1 minute
            await asyncio.sleep(60)
            os.remove(str(video_path))

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")
