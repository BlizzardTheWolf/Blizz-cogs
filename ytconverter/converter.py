import os
import discord
from redbot.core import commands
from pytube import YouTube
import aiohttp
import asyncio
import time

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = self.bot.cog_data_path(self)

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            await ctx.send("Converting the video to MP3, please wait...")
            await self.download_and_convert(ctx, url, only_audio=True)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

    @commands.command()
    async def ytmp4(self, ctx, url):
        try:
            await ctx.send("Converting the video to mp4, please wait...")
            await self.download_and convert(ctx, url, only_audio=False)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

    async def download_and_convert(self, ctx, url, only_audio):
        yt = YouTube(url)

        if yt.age_restricted:
            await ctx.send("This video is age-restricted and cannot be converted.")
            return

        stream = yt.streams.filter(only_audio=only_audio).first()

        if not stream:
            await ctx.send("Could not find a suitable stream for download.")
            return

        filename = f'{yt.video_id}.{"mp3" if only_audio else "mp4"}'

        audio_path = os.path.join(self.data_path, filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(stream.url) as response:
                data = await response.read()

        with open(audio_path, 'wb') as file:
            file.write(data)

        await asyncio.sleep(5)

        user = ctx.author
        await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted {"audio" if only_audio else "video"}:', file=discord.File(audio_path))

        # Remove the file after 10 minutes
        await asyncio.sleep(600)
        os.remove(audio_path)

def setup(bot):
    bot.add_cog(ConverterCog(bot))
