import discord
from discord.ext import commands
from pytube import YouTube
import moviepy.editor as mp
import os

class YTMP4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def convert(self, ctx, url, format="mp4"):
        format = format.lower()  # Convert the format argument to lowercase
        if format not in ["mp4", "mp3"]:
            await ctx.send("Invalid format. Please use 'mp4' or 'mp3'.")
            return

        try:
            yt = YouTube(url)

            if yt.age_restricted:
                await ctx.send("This video is age-restricted and cannot be converted.")
                return

            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            if not stream:
                await ctx.send("Could not find a suitable video stream for download.")
                return

            duration = yt.length

            if duration > max_video_duration:
                await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
                return

            await ctx.send("Converting the video, please wait...")

            video_path = f'video-{ctx.author.id}.mp4'
            stream.download(output_path='/mnt/converter', filename=video_path)

            if os.path.getsize(video_path) > max_file_size_bytes:
                await ctx.send("The file is too big to be converted. It must be under 25MBs. This is Discord's fault, not mine.")
                os.remove(video_path)
                return

            if format == "mp3":
                mp3_path = f'audio-{ctx.author.id}.mp3'

                video_clip = mp.VideoFileClip(video_path)
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(mp3_path)
                audio_clip.close()
                video_clip.close()

                await ctx.send(f'{ctx.author.mention}, your video conversion is complete. Here is the converted audio:', file=discord.File(mp3_path))
                os.remove(mp3_path)
            else:
                await asyncio.sleep(5)
                user = ctx.message.author
                await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted video:', file=discord.File(video_path))

            os.remove(video_path)
        except Exception as e:
            error_message = str(e)
            await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
