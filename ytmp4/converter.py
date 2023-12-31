import os
import discord
from redbot.core import commands
from pytube import YouTube
import asyncio
import time
from redbot.core.data_manager import cog_data_path  # Import the data manager

class YTMP4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = cog_data_path(self)  # Use the cog_data_path for this cog

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

            await ctx.send("Converting the video to mp4, please wait...")

            # Generate a unique filename with timestamp
            video_code = str(int(time.time())) + ".mp4"
            video_path = self.data_path / "converter" / video_code
            output_video_path = video_path.with_suffix(".mp4")

            stream.download(output_path=str(self.data_path / "converter"), filename=video_code)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to mp4 is complete. Here is the converted video:', file=discord.File(output_video_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(output_video_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
