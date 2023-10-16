import os
import discord
from redbot.core import commands
import asyncio
from pytube import YouTube
from moviepy.editor import *

class YTMP3Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                await ctx.send("Could not find a suitable audio stream for download.")
                return

            await ctx.send("Downloading the audio, please wait...")
            
            # Generate a unique filename based on video title and user ID
            video_title = f"{yt.title}-{ctx.author.id}"
            
            # Download the video stream
            stream.download(output_path="/mnt/converter", filename=f"{video_title}.temp")
            
            # Convert the video to audio
            clip = VideoFileClip(f"/mnt/converter/{video_title}.temp")
            clip.audio.write_audiofile(f"/mnt/converter/{video_title}.mp3")
            
            # Remove the temporary video file
            os.remove(f"/mnt/converter/{video_title}.temp")
            
            await asyncio.sleep(5)
            user = ctx.message.author
            await ctx.send(f"{user.mention}, your audio conversion is complete. Here is the converted audio:",
                           file=discord.File(f"/mnt/converter/{video_title}.mp3"))

            # Remove the audio file after 10 minutes
            await asyncio.sleep(600)
            os.remove(f"/mnt/converter/{video_title}.mp3")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP3Cog(bot))
