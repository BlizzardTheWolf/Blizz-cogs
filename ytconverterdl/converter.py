import discord
from redbot.core import commands
from yt_dlp import YoutubeDL
import aiohttp
from aiohttp import web
import asyncio
from redbot.core import data_manager
from pathlib import Path

class YTConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)
        self.app = web.Application()
        self.app.router.add_route('GET', '/videos/{filename}', self.handle_video_request)
        self.runner = web.AppRunner(self.app)
        self.hostname = None  # Store the hostname for web server
        self.port = 8080  # Default port
        asyncio.create_task(self.start_server())

    async def start_server(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, '0.0.0.0', self.port)
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
                'format': 'bestvideo[height<=?1080]+bestaudio/best' if not to_mp3 else 'bestaudio/best',
                'outtmpl': str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}"),
            }

            # Send "Converting..." message
            conversion_message = await ctx.send(f"`Converting...`")

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

                if 'entries' in info_dict:
                    ydl_opts['outtmpl'] = str(output_folder / f"%(id)s.{'mp3' if to_mp3 else 'webm'}")

                    ydl.download([url])

                    # Update message to indicate uploading
                    await conversion_message.edit(content=f"`Uploading...`")
                    video_id = info_dict['entries'][0]['id']
                    file_path = output_folder / f"{video_id}.{'mp3' if to_mp3 else 'webm'}"

                    # Serve the video using aiohttp
                    download_link = f"http://{self.hostname}:{self.port}/videos/{video_id}"
                    await ctx.send(f"{ctx.author.mention} `Done | Download Link: {download_link}`")

                    # Remove the file after 1 minute if it exists
                    await asyncio.sleep(60)
                    if file_path.exists():
                        file_path.unlink()
                    return

            raise ValueError("No suitable format available for download.")

        except Exception as e:
            error_message = str(e)
            await ctx.send(f"{ctx.author.mention} `An error occurred during conversion. {error_message}`")

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

    @commands.command()
    @commands.is_owner()
    async def ytcset(self, ctx, hostname: str, port: int = 8080):
        """
        Set the hostname and port for the web server.
        """
        self.hostname = hostname
        self.port = port
        await ctx.send(f"Hostname set to {hostname}, Port set to {port}")

    @commands.command()
    async def ytcurl(self, ctx, video_id):
        """
        Get the download URL for a converted video.
        """
        download_link = f"http://{self.hostname}:{self.port}/videos/{video_id}"
        await ctx.send(f"{ctx.author.mention} `Download Link: {download_link}`")
