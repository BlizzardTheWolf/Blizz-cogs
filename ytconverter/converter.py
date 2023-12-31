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
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'mp4'}"),
                'default_search': 'auto',  # Set default search
                'progress_hooks': [self.my_hook],  # Add progress hook
            }

            conversion_message = await ctx.send(f"`Converting video...`")

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Wait for the download and conversion to complete
            await asyncio.sleep(5)

            user = ctx.message.author
            downloaded_file_path = output_folder / f"{ydl.extract_info(url)['id']}.{'mp3' if to_mp3 else 'mp4'}"
            renamed_file_path = output_folder / f"{ydl.extract_info(url)['id']}.{'mp3' if to_mp3 else 'mp4'}"

            # Check if the downloaded file exists before renaming
            if downloaded_file_path.exists():
                downloaded_file_path.rename(renamed_file_path)

                # Try uploading the file
                try:
                    await conversion_message.edit(content=f"`Uploading video...`")
                    # Send a new message with the converted file, mentioning the user
                    await ctx.send(f'{user.mention}, `Here is the converted video:`',
                                   file=discord.File(str(renamed_file_path)))
                    await conversion_message.edit(content=f"`Video uploaded successfully.`")
                except discord.errors.HTTPException as upload_error:
                    # If uploading fails, send an error message
                    await ctx.send(f"`An error occurred during upload. Please check the file and try again.\nError details: {upload_error}`")
            else:
                await ctx.send("`An error occurred during conversion. The downloaded file does not exist.`")

            # Remove the file after 10 minutes if it exists
            if renamed_file_path.exists():
                renamed_file_path.unlink()

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"`An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

    def my_hook(self, d):
        if d['status'] == 'finished':
            print('Done downloading, now converting...')

    @commands.command()
    async def ytmp3(self, ctx, *, query):
        """
        Converts a YouTube video to MP3.

        Parameters:
        `<query>` The search query or URL of the video you want to convert.
        """
        await self.download_and_convert(ctx, query, to_mp3=True)

    @commands.command()
    async def ytmp4(self, ctx, *, query):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<query>` The search query or URL of the video you want to convert.
        """
        await self.download_and_convert(ctx, query, to_mp3=False)
