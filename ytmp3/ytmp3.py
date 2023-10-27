import os
import discord
from redbot.core import commands
from pytube import YouTube
import asyncio
from redbot.core.data_manager import cog_data_path  # Import the data manager

class YTMP3Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = cog_data_path(self)  # Use the cog_data_path for this cog

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            stream = yt.streams.filter(only_audio=True).first()

            if not stream:
                await ctx.send("Could not find an audio stream for download.")
                return

            await ctx.send("Converting the video to MP3, please wait...")

            # Get the video code from the YouTube URL
            video_code = yt.video_id

            audio_path = self.data_path / "converter" / video_code
            output_audio_path = audio_path.with_suffix(".mp3")

            # Download the audio without an extension
            stream.download(output_path=str(self.data_path / "converter"), filename=video_code)

            # Rename the file with .mp3 extension
            os.rename(audio_path, output_audio_path)

            audio_path = output_audio_path

            await asyncio.sleep(5)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to MP3 is complete. Here is the converted audio:', file=discord.File(audio_path))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(audio_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP3Cog(bot))
