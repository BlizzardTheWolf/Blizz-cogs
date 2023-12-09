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

    async def download_and_convert_with_dropdown(self, ctx, url, to_mp3=False):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            conversion_message = await ctx.send(f"`Getting available qualities...`")

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info['formats']
                quality_view = discord.ui.Select(
                    placeholder = "Quality options",
                    options = formats
                )
                message = await ctx.send("Please select the preferred video quality:", view=quality_view)  # Post message with dropdown
                selected_format = await quality_view.wait()
                await asyncio.sleep(120)

                ydl_opts['format'] = selected_format  # Update the format based on user selection

                await message.edit(content=f"`Converting video to {selected_format}...`")

                ydl.download([url])

            await asyncio.sleep(5)

            user = ctx.message.author
            downloaded_file_path = output_folder / f"{info['id']}.{'mp3' if to_mp3 else 'webm'}"
            renamed_file_path = output_folder / f"{info['id']}.{'mp3' if to_mp3 else 'mp4'}"
            
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

            # Remove the file after 10 minutes if it exists
            if renamed_file_path.exists():
                renamed_file_path.unlink()
        except Exception as e:
            error_message = str(e)
            await ctx.send(f"`An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

    @commands.command()
    async def ytmp3(self, ctx, url):
        """
        Converts a YouTube video to MP3.

        Parameters:
        `<url>` The URL of the video you want to convert.
        """
        await self.download_and_convert_with_dropdown(ctx, url, to_mp3=True)

    @commands.command()
    async def ytmp4(self, ctx, url):
        """
        Converts a YouTube video to MP4.

        Parameters:
        `<url>` The URL of the video you want to convert.
        """
        await self.download_and_convert_with_dropdown(ctx, url, to_mp3=False)
