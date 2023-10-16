import os
import discord
from redbot.core import commands
from pytube import YouTube
import asyncio
from datetime import timezone

class YTMP4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not os.path.exists('/mnt/converter'):
            os.makedirs('/mnt/converter')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name}')

    @commands.command()
    async def convert(self, ctx, url, format='mp4'):
        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            stream = yt.streams.filter(progressive=True, file_extension=format).order_by('resolution').desc().first()

            if not stream:
                await ctx.send("Could not find a suitable video stream for download.")
                return

            duration = yt.length

            if duration > 600:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.trigger_typing()  # Show "typing" status while converting

            video_path = f'/mnt/converter/{yt.title}-{ctx.author.id}.{format}'
            stream.download(output_path='/mnt/converter', filename=yt.title)
            file_size = os.path.getsize(video_path)

            if file_size > 25 * 1024 * 1024:  # 25MB
                os.remove(video_path)
                await ctx.send("The file is too big to be converted. It must be under 25MBs. This is Discord's fault, not mine.")
                return

            if format == 'mp3':
                os.system(f'ffmpeg -i "{video_path}" -vn -ab 192k -ar 44100 -y "{video_path[:-4]}.mp3"')
                os.remove(video_path)
                video_path = f'/mnt/converter/{yt.title}-{ctx.author.id}.mp3'

            user = ctx.author
            await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted file:', file=discord.File(video_path))
        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

    # ... (other bot commands, if any)

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
