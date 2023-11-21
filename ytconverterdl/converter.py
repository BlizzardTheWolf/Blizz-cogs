import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
import os
from redbot.core import data_manager

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def convert_and_send(self, ctx, url, to_mp3, output_folder):
        try:
            ydl_opts = {
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo+bestaudio/best',
                'outtmpl': str(output_folder / "%(title)s.%(ext)s"),
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    video_info = info_dict['entries'][0]
                else:
                    video_info = info_dict

                ydl.download([url])

            user = ctx.message.author
            file_path = output_folder / f"{video_info['title']}.{video_info['ext']}"

            await ctx.send("Please wait, the video is being converted...")

            await asyncio.sleep(5)  # Simulate conversion time

            await ctx.send(f'{user.mention}, your video conversion to {"MP3" if to_mp3 else "MP4"} is complete. Here is the converted file:',
                           file=discord.File(str(file_path)))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            file_path.unlink()

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}")

    @commands.command()
    async def ytmp3(self, ctx, url):
        """
        Converts a YouTube video to MP3.

        Parameters:
        `<url>` The URL of the video you want to convert.
        """
        output_folder = self.data_folder / "mp3"
        self.bot.loop.create_task(self.convert_and_send(ctx, url, to_mp3=True, output_folder=output_folder))

    @commands.command()
    async def ytmp4(self, ctx, url):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<url>` The URL of the video you want to convert.
        """
        output_folder = self.data_folder / "mp4"
        self.bot.loop.create_task(self.convert_and_send(ctx, url, to_mp3=False, output_folder=output_folder))
