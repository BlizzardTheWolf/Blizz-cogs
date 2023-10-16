import os
import discord
from redbot.core import commands
import asyncio
from pytube import YouTube

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
                await ctx.send("Could not find a suitable MP4 stream for download.")
                return

            duration = yt.length

            if duration > 600:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send("Converting the video to MP4, please wait...")

            # Extract the video code from the URL
            video_code = yt.video_id
            video_path = f'/mnt/converter/{video_code}.mp4'
            stream.download(output_path="/mnt/converter", filename=video_code)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to MP4 is complete. Here is the converted video:', file=discord.File(video_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(video_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
