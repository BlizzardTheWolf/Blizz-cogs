import os
import discord
from redbot.core import commands
import asyncio

class YTMP3Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            mp3_filename = await self.download_mp3(url)

            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to MP3 is complete. Here is the MP3 audio:', file=discord.File(mp3_filename))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(mp3_filename)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

    async def download_mp3(self, url):
        mp3_filename = "/mnt/converter/audio.mp3"  # Adjust the filename and path as needed
        command = f"yt-dl --extract-audio --audio-format mp3 -o '{mp3_filename}' '{url}'"

        try:
            # Run the yt-dl command to download and convert the video to MP3
            os.system(command)
            return mp3_filename
        except Exception as e:
            raise e

def setup(bot):
    bot.add_cog(YTMP3Cog(bot))
