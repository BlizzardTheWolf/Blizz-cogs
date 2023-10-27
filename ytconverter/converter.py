import discord
from redbot.core import commands
from youtube_dl import YoutubeDL
import os
import asyncio
import time

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.converter_dir = os.path.join(str(self.bot.cog_data_path(self)), "downloads")

    @commands.Cog.listener()
    async def cog_check(self, ctx):
        if not ctx.author.bot:
            return True

    async def download_and_convert(self, ctx, url, only_audio):
        ydl_opts = {
            "format": "bestaudio" if only_audio else "best",
            "outtmpl": os.path.join(self.converter_dir, "%(title)s.%(ext)s"),
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.join(self.converter_dir, info["_filename"])
            return filename

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            await ctx.send("Converting the video to MP3, please wait...")
            audio_path = await self.download_and_convert(ctx, url, only_audio=True)

            user = ctx.author
            await ctx.send(f'{user.mention}, your video conversion to MP3 is complete. Here is the converted audio:', file=discord.File(audio_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(audio_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

    @commands.command()
    async def ytmp4(self, ctx, url):
        try:
            await ctx.send("Converting the video to mp4, please wait...")
            video_path = await self.download_and_convert(ctx, url, only_audio=False)

            user = ctx.author
            await ctx.send(f'{user.mention}, your video conversion to mp4 is complete. Here is the converted video:', file=discord.File(video_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(video_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")
