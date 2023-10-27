import discord
from redbot.core import commands
from pytube import YouTube
import asyncio
import time
import os
from redbot.core import data_manager
import shutil

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, to_mp3=False):
        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            stream = yt.streams.filter(only_audio=to_mp3).first() if to_mp3 else yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()

            if not stream:
                await ctx.send("Could not find a suitable stream for download.")
                return

            duration = yt.length

            if to_mp3:
                output_ext = ".mp3"
                output_folder = self.data_folder / "mp3"
            else:
                output_ext = ".mp4"
                output_folder = self.data_folder / "mp4"

            if duration > 600:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send(f"Converting the video to {output_ext}, please wait...")

            # Generate a unique filename with timestamp
            video_code = str(int(time.time())) + output_ext
            video_path = output_folder / video_code

            stream.download(output_path=str(output_folder), filename=video_code)

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to {output_ext} is complete. Here is the converted file:',
               file=discord.File(str(video_path)))


            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            video_path.unlink()

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}")

    @commands.command()
    async def ytmp3(self, ctx, url):
        await self.download_and_convert(ctx, url, to_mp3=True)

    @commands.command()
    async def ytmp4(self, ctx, url):
        await self.download_and_convert(ctx, url, to_mp3=False)

    # Rest of your code here...

def setup(bot):
    bot.add_cog(ConverterCog(bot))
