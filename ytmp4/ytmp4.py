import discord
from discord.ext import commands
from pytube import YouTube
import moviepy.editor as mp
import os

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

            stream = yt.streams.filter(progressive=True, file_extension=format).order_by('resolution').desc().first()

            if not stream:
                await ctx.send("Could not find a suitable video stream for download.")
                return

            duration = yt.length

            if duration > max_video_duration:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send("Converting the video, please wait...")

            video_path = f'/mnt/converter/{yt.title}-{ctx.author.id}.{format}'  # Updated path
            stream.download(output_path='/mnt/converter/', filename=video_path)

            if os.path.getsize(video_path) > max_file_size_bytes:
                await ctx.send("The file is too big to be converted. It must be under 25MBs. This is Discord's fault, not mine.")
                os.remove(video_path)
                return

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted video:', file=discord.File(video_path))
        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
