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
                'format': 'bestvideo[height<=720]+bestaudio/best' if not to_mp3 else 'bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            conversion_message = await ctx.send(f"`Downloading...`")

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    # Get available formats and sort by quality
                    formats = sorted(info_dict['entries'][0]['formats'], key=lambda x: x['height'] if 'height' in x else float('inf'), reverse=True)
                    
                    # Find the first format with video
                    video_format = next((f for f in formats if 'height' in f), None)

                    if video_format:
                        ydl_opts['format'] = f"{video_format['format_id']}/bestaudio/best" if not to_mp3 else 'bestaudio/best'
                        ydl_opts['outtmpl'] = str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}")

                        # Download using the chosen format
                        ydl.download([url])

                        await conversion_message.edit(content=f"`Uploading...`")
                        # Send a new message with the converted file
                        file_path = output_folder / f"{info_dict['entries'][0]['id']}.{'mp3' if to_mp3 else 'webm'}"
                        file_size = file_path.stat().st_size
                        await ctx.send(f"{ctx.author.mention} `Done | Size: {file_size / (1024 * 1024):.2f} MB`", file=discord.File(str(file_path)))

                        # Remove the file after 1 minute if it exists
                        await asyncio.sleep(60)
                        if file_path.exists():
                            file_path.unlink()
                        return

            # If no suitable format found
            raise ValueError("No suitable format available for download.")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"{ctx.author.mention} `An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

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
