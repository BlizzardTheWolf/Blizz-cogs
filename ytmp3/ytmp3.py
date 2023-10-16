import os
import discord
from redbot.core import commands
import asyncio
import youtube_dl

class YTMP3Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ytmp3(self, ctx, url):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'/mnt/converter/%(title)s-{ctx.author.id}.mp3',
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', 'video')

                await ctx.send("Converting the video to MP3, please wait...")

                ydl.download([url])

            await asyncio.sleep(5)
            user = ctx.message.author
            await ctx.send(f'{user.mention}, your video conversion to MP3 is complete. Here is the converted audio:', file=discord.File(f"/mnt/converter/{video_title}-{ctx.author.id}.mp3"))

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            os.remove(f"/mnt/converter/{video_title}-{ctx.author.id}.mp3")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during audio conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP3Cog(bot))
