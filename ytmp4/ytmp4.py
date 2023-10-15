import os
import discord
from redbot.core import commands
from pytube import YouTube
import asyncio

class YTMP4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def convert(self, ctx, url, format="mp4"):
        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            if format not in ("mp4", "mp3"):
                await ctx.send("Invalid format. Please specify either 'mp4' or 'mp3'.")
                return

            stream = yt.streams.filter(progressive=True, file_extension=format).order_by('resolution').desc().first()

            if not stream:
                await ctx.send(f"Could not find a suitable {format} stream for download.")
                return

            duration = yt.length

            if duration > 600:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send(f"Converting the video to {format}, please wait...")
            video_path = f'{yt.title}-{ctx.author.id}.{format}'
            stream.download(output_path="/mnt/converter", filename=video_path)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to {format} is complete. Here is the converted video:', file=discord.File(f"/mnt/converter/{video_path}"))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(f"/mnt/converter/{video_path}")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
