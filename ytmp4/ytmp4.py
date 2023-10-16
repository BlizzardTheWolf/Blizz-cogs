import discord
from redbot.core import commands
import asyncio
from redbot.core.bot import Red
import os
from moviepy.editor import VideoFileClip
from pytube import YouTube

class YTMP4Cog(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.command()
    async def convert(self, ctx: commands.Context, url: str, output_format: str = "mp4"):
        valid_formats = ["mp4", "mp3"]
        output_format = output_format.lower()

        if output_format not in valid_formats:
            await ctx.send("Invalid output format. Please use 'mp4' or 'mp3'.")
            return

        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()

            if not stream:
                await ctx.send("Could not find a suitable video stream for download.")
                return

            video_path = f'/mnt/converter/{yt.title}-u{ctx.author.id}.{output_format}'

            stream.download(filename=video_path)

            if os.path.getsize(video_path) > 25 * 1024 * 1024:
                await ctx.send("The file is too big to be converted. It must be under 25MB. This is Discord's file size limit.")
                os.remove(video_path)
                return

            if output_format == "mp3":
                video = VideoFileClip(video_path)
                audio_path = video_path.replace(".mp4", ".mp3")
                video.audio.write_audiofile(audio_path, verbose=False)
                os.remove(video_path)
                video_path = audio_path

            await asyncio.sleep(5)
            user = ctx.author
            await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted video:', file=discord.File(video_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(video_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot: Red):
    bot.add_cog(YTMP4Cog(bot))
