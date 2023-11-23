import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import aiohttp
from aiohttp import web
import asyncio
from redbot.core import data_manager
from pathlib import Path

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)
        self.app = web.Application()
        self.app.router.add_route('GET', '/videos/{filename}', self.handle_video_request)
        self.runner = web.AppRunner(self.app)
        asyncio.create_task(self.start_server())

    async def start_server(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, '0.0.0.0', 8080)  # Change the port as needed
        await site.start()

    async def handle_video_request(self, request):
        filename = request.match_info['filename']
        video_path = self.data_folder / filename
        if video_path.exists():
            with open(video_path, 'rb') as f:
                response = web.StreamResponse()
                response.content_type = 'video/mp4'  # Change the content type based on your file type
                await response.prepare(request)
                await response.write(f.read())
                return response
        else:
            return web.Response(status=404)

    async def download_and_convert(self, ctx, url, to_mp3=False):
        try:
            output_folder = self.data_folder / ("mp3" if to_mp3 else "mp4")

            ydl_opts = {
                'format': 'bestvideo+bestaudio/best' if not to_mp3 else 'bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            # Send "Converting..." message
            conversion_message = await ctx.send(f"`Converting...`")

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    ydl_opts['format'] = info_dict['entries'][0]['format_id']
                    ydl_opts['outtmpl'] = str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}")

                    ydl.download([url])

                    # Update message to indicate uploading
                    await conversion_message.edit(content=f"`Uploading...`")
                    video_id = info_dict['entries'][0]['id']
                    file_path = output_folder / f"{video_id}.{'mp3' if to_mp3 else 'webm'}"

                    # Check file size and duration
                    file_size = file_path.stat().st_size
                    file_duration = info_dict['entries'][0].get('duration', 0)

                    if file_size <= 250 * 1024 * 1024 and file_duration <= 900:  # 250 MB and 15 minutes
                        # Serve the video using aiohttp
                        download_link = f"http://yourserverip:8080/videos/{video_id}"
                        await ctx.send(f"{ctx.author.mention} `Done | Download Link: {download_link}`")
                    else:
                        # File exceeds size limit
                        await ctx.send(
                            f"{ctx.author.mention} `File exceeds size limit. Size: {file_size / (1024 * 1024):.2f} MB. Removing...`"
                        )
                        if file_path.exists():
                            file_path.unlink()

                    # Remove the file after 1 minute if it exists
                    await asyncio.sleep(60)
                    if file_path.exists():
                        file_path.unlink()
                    return

            raise ValueError("No suitable format available for download.")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"{ctx.author.mention} `An error occurred during conversion. Please check the URL and try again.\nError details: {error_message}`")

    @commands.command()
    async def ytmp3(self, ctx, url):
        await self.download_and_convert(ctx, url, to_mp3=True)

    @commands.command()
    async def ytmp4(self, ctx, url):
        await self.download_and_convert(ctx, url, to_mp3=False)
