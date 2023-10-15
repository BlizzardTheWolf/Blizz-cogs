import os
import discord
from redbot.core import commands
from pytube import YouTube
import asyncio

class YTMP4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def convert(self, ctx, url):
        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            if not stream:
                await ctx.send("Could not find a suitable video stream for download.")
                return

            duration = yt.length

            if duration > 600:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send("Converting the video, please wait...")
            video_path = f'{yt.title}-{ctx.author.id}.mp4'
            stream.download(output_path="/mnt/converter", filename=video_path)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted video:', file=discord.File(f"/mnt/converter/{video_path}"))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(f"/mnt/converter/{video_path}")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
