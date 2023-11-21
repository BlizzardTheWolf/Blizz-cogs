import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, to_mp3=False):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo[ext=mp4]+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            async with ctx.typing(ephemeral=False):  # Start typing indication
                await ctx.send("Please wait, the video is being converted...")

                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)

                    if 'entries' in info_dict:
                        video_info = info_dict['entries'][0]
                    else:
                        video_info = info_dict

                    ydl.download([url])

                await asyncio.sleep(5)

                user = ctx.message.author
                downloaded_file_path = output_folder / f"{video_info['id']}.{'mp3' if to_mp3 else 'webm'}"
                renamed_file_path = output_folder / f"{video_info['id']}.{'mp3' if to_mp3 else 'mp4'}"

                downloaded_file_path.rename(renamed_file_path)

                await ctx.send(f'{user.mention}, your video conversion to {"MP3" if to_mp3 else "MP4"} is complete. Here is the converted file:',
                            file=discord.File(str(renamed_file_path)))

                # Remove the file after 10 minutes if it exists
                await asyncio.sleep(600)
                if renamed_file_path.exists():
                    renamed_file_path.unlink()

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
        await self.download_and_convert(ctx, url, to_mp3=True)

    @commands.command()
    async def ytmp4(self, ctx, url):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<url>` The URL of the video you want to convert.
        """
        await self.download_and_convert(ctx, url, to_mp3=False)
