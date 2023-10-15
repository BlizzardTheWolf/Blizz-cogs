import discord
from redbot.core import commands
from pytube import YouTube
import asyncio
import os

class YouTubeConverter(commands.Cog):
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

            user_video_folder = os.path.join('/mnt/converter', f'video_{ctx.author.id}')
            os.makedirs(user_video_folder, exist_ok=True)

            video_path = os.path.join(user_video_folder, f'{yt.title}-{ctx.author.id}.mp4')
            stream.download(output_path=user_video_folder, filename=f'{yt.title}-{ctx.author.id}.mp4')

            if os.path.getsize(video_path) > 25 * 1024 * 1024:
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
    bot.add_cog(YouTubeConverter(bot))
