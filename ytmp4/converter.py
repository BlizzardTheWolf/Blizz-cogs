import os
import discord
from redbot.core import commands
import asyncio
from pytube import YouTube
from moviepy.editor import VideoFileClip

class YTMP4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

            if duration > 600:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send(f"Converting the video to mp4, please wait...")
            video_path = f'{yt.title}-{ctx.author.id}.mp4'
            stream.download(output_path="/mnt/converter", filename=video_path)

            # Perform transcoding using moviepy
            input_path = f"/mnt/converter/{video_path}"
            output_path = f"/mnt/converter/{yt.title}-{ctx.author.id}-transcoded.mp4"
            clip = VideoFileClip(input_path)
            clip.write_videofile(output_path, codec="libx264")

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to mp4 is complete. Here is the converted video:', file=discord.File(output_path))

            # Remove the files after sending
            os.remove(input_path)
            os.remove(output_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
