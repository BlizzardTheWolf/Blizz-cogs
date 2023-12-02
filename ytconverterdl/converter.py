import discord
from discord.ext import commands, menus
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path

class VideoQualityMenu(menus.Menu):
    def __init__(self, qualities, original_message, ctx):
        super().__init__(timeout=120, delete_message_after=True)
        self.qualities = qualities
        self.original_message = original_message
        self.ctx = ctx

    async def send_initial_message(self, ctx, channel):
        return await channel.send(
            f"Select the preferred video quality:",
            view=self
        )

    async def format_page(self, menu, page):
        return discord.Embed(
            title="Video Quality Selection",
            description="\n".join(f"{i}. {quality}" for i, quality in enumerate(self.qualities, start=1)),
            color=discord.Color.blurple()
        )

    async def on_timeout(self):
        await self.original_message.edit(content="Video quality selection timeout. Please run the command again.")

    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot interact with this menu.", ephemeral=True)
            return False
        return True

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def on_select_button(self, payload):
        await self.original_message.edit(content="Converting video...")

        try:
            selected_index = int(payload.component.label) - 1
            selected_quality = self.qualities[selected_index]

            await self.original_message.edit(content=f"Converting video to {selected_quality}...")

            # Your conversion logic here
            output_folder = Path.cwd() / "output"
            output_folder.mkdir(parents=True, exist_ok=True)

            ydl_opts = {
                'format': selected_quality,
                'outtmpl': str(output_folder / f"%(title)s.{'mp4'}"),
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            user = self.ctx.message.author
            downloaded_file_path = output_folder / f"{video_info['title']}.mp4"
            renamed_file_path = output_folder / f"{video_info['title']}.mp4"

            # Simulating successful conversion and upload
            await asyncio.sleep(5)
            await self.original_message.edit(content="Successful")
            await self.ctx.send(f'{user.mention}, `Here is the converted video:`',
                                file=discord.File(str(renamed_file_path)))
        except Exception as e:
            error_message = f"An error occurred during conversion. Error details: {str(e)}"
            await self.ctx.send(f"`{error_message}`")

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)

    async def download_and_convert(self, ctx, url, to_mp3=False):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestaudio/best' if to_mp3 else 'bestvideo+bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            conversion_message = await ctx.send(f"`Converting video...`")

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

            # Get available video qualities
            qualities = [stream['format_note'] for stream in video_info['formats']]

            if qualities:
                # Display a dropdown menu for quality selection
                view = VideoQualityMenu(qualities, conversion_message, ctx)
                await view.start(ctx)
            else:
                await conversion_message.edit(content="No available video qualities.")
        except Exception as e:
            error_message = f"An error occurred during conversion. Error details: {str(e)}"
            await ctx.send(f"`{error_message}`")

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
