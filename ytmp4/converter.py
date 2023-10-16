from redbot.core import commands
from pytube import YouTube
from moviepy.editor import VideoFileClip
import discord
import os

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.max_video_duration = 600
        self.max_file_size_bytes = 25 * 1024 * 1024

    @commands.command()
    async def convert(self, ctx, url, format='mp4'):
        user = ctx.author
        await ctx.trigger_typing()  # Show "typing" status while converting

        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            if format not in ['mp4', 'mp3']:
                await ctx.send("Invalid format. Supported formats are 'mp4' and 'mp3'.")
                return

            stream = yt.streams.filter(progressive=True, file_extension=format).order_by('resolution').desc().first()

            if not stream:
                await ctx.send(f"Could not find a suitable {format} stream for download.")
                return

            duration = yt.length

            if duration > self.max_video_duration:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send(f"Converting the video to {format}, please wait...")

            video_path = f'video.{format}'
            stream.download(filename=video_path)

            if os.path.getsize(video_path) > self.max_file_size_bytes:
                await ctx.send(f"The file is too big to be converted. It must be under 25MBs. This is Discord's fault, not mine.")
                os.remove(video_path)
                return

            if format == 'mp3':
                audio_path = 'audio.mp3'
                clip = VideoFileClip(video_path)
                clip.audio.write_audiofile(audio_path, codec='mp3')
                clip.close()

                await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted audio:', file=discord.File(audio_path))

                os.remove(audio_path)
            else:
                await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted video:', file=discord.File(video_path))

            os.remove(video_path)

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(ConverterCog(bot))
