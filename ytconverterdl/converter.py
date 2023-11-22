import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import asyncio
from redbot.core import data_manager
from pathlib import Path
from flask import Flask, send_file
import threading

app = Flask(__name__)

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.video_path = "videos/"
        self.server_thread = threading.Thread(target=app.run, kwargs={"port": 4090})
        self.server_thread.start()

    def cog_unload(self):
        # Stop the Flask server thread when the cog is unloaded
        self.server_thread.join()

    @commands.command()
    async def ytmp4(self, ctx, url):
        try:
            output_folder = self.video_path
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio/best',
                'outtmpl': str(output_folder / "%(id)s.{'mp4'}"),
            }

            conversion_message = await ctx.send("`Video is being processed...`")

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    video_info = info_dict['entries'][0]
                else:
                    video_info = info_dict

                ydl.download([url])

            await asyncio.sleep(5)

            video_id = video_info['id']
            video_filename = f"{video_id}.mp4"
            video_path = Path(self.video_path) / video_filename

            await ctx.send(f"Here is your video: http://web.purplepanda.cc:4090/{video_filename}")

            # Remove the file after 10 minutes
            await asyncio.sleep(600)
            try:
                # Remove the file if it exists
                if video_path.exists():
                    video_path.unlink()
            except Exception as e:
                print(f"Error removing video file: {e}")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"`An error occurred during video processing. Please check the URL and try again.\nError details: {error_message}`")
