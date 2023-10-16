import os
import discord
from redbot.core import commands
from pytube import YouTube
from moviepy.editor import VideoFileClip
import asyncio
import re

class YTMP3Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

            # Sanitize the video title
            title = re.sub(r'[\/:*?"<>|]', '', yt.title)
            title = title.replace(" ", "_")  # Replace spaces with underscores
            video_path = f'/mnt/converter/{title}-{ctx.author.id}.mp4'
            audio_path = f'/mnt/converter/{title}-{ctx.author.id}.mp3'

            video_stream = yt.streams.get_highest_resolution()
            video_stream.download(output_path="/mnt/converter")

            clip = VideoFileClip(video_path)
            clip.audio.write_audiofile(audio_path)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to MP3 is complete. Here is the converted audio:', file=discord.File(audio_path))

            # Remove the files after 10 minutes
            await asyncio.sleep(600)
            os.remove(video_path)
            os.remove(audio_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP3Cog(bot))
