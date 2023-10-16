import discord
from discord.ext import commands
from pytube import YouTube
import asyncio
import os
import traceback
import datetime

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

maintenance_user_id = 1071559067975295058
maintenance_mode = False
max_video_duration = 600
max_file_size_bytes = 25 * 1024 * 1024

if not os.path.exists('error_log.txt'):
    with open('error_log.txt', 'w'):
        pass

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="!convert"))

@bot.event
async def on_error(event, *args, **kwargs):
    error_message = traceback.format_exc()
    print(f'Bot went down due to an error at {datetime.datetime.now()}:\n{error_message}')
    with open('error_log.txt', 'w') as error_log:
        error_log.write(error_message)

@bot.command()
async def convert(ctx, url, filetype="mp4"):
    try:
        yt = YouTube(url)

        if yt.age_restricted:
            await ctx.send("This video is age-restricted and cannot be converted.")
            return

        stream = yt.streams.filter(progressive=True, file_extension=filetype).order_by('resolution').desc().first()

        if not stream:
            await ctx.send("Could not find a suitable video stream for download.")
            return

        duration = yt.length

        if duration > max_video_duration:
            await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
            return

        await ctx.trigger_typing()  # Show "typing" status while converting

        await ctx.send("Converting the video, please wait...")
        video_path = 'video.mp4'
        stream.download(output_path='/mnt/converter', filename=f"{yt.title}-{ctx.author.id}")

        if os.path.getsize(video_path) > max_file_size_bytes:
            await ctx.send("The file is too big to be converted. It must be under 25MBs. This is Discord's fault, not mine.")
            os.remove(video_path)
            return

        await asyncio.sleep(5)

        user = ctx.message.author
        await ctx.send(f'{user.mention}, your video conversion is complete. Here is the converted video:', file=discord.File(video_path))
    except Exception as e:
        error_message = str(e)
        await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")

# ...
