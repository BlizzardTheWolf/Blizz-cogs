from redbot.core import commands, data_manager
import discord
import aiohttp
import yt_dlp
import asyncio
from pathlib import Path
import os

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)
        self.app = aiohttp.web.Application()
        self.runner = aiohttp.web.AppRunner(self.app)
        self.hostname = "web.purplepanda.cc"
        self.port = 4090
        self.is_server_running = False
        self.start_server_task = None

    async def start_server(self):
        await self.bot.wait_until_ready()

        if not self.is_server_running:
            self.app.router.add_route('GET', '/videos/{filename}', self.handle_video_request)
            site = aiohttp.web.TCPSite(self.runner, self.hostname, self.port)

            await self.runner.setup()
            await site.start()

            self.is_server_running = True

    async def handle_video_request(self, request):
        filename = request.match_info.get('filename', '')
        video_path = Path(self.data_folder) / filename
        if not video_path.is_file() or not video_path.parts[:len(Path(self.data_folder).parts)] == Path(self.data_folder).parts:
            raise aiohttp.web.HTTPNotFound()

        with open(video_path, 'rb') as f:
            return aiohttp.web.Response(body=f.read(), content_type='audio/mpeg' if video_path.suffix == '.mp3' else 'video/mp4')

    async def download_and_convert(self, ctx, url, format):
        ydl_opts = {
            'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio/best',
            'outtmpl': f'{self.data_folder}/%(id)s.%(ext)s',
        }

        await ctx.send(f"Converting to {format}... This may take a moment.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

        return filename

    @commands.command()
    async def ytmp3(self, ctx, url):
        filename = await self.download_and_convert(ctx, url, 'mp3')
        download_url = await self.get_download_url(filename)
        await ctx.send(f"Conversion complete! You can download the MP3 [here]({download_url}) {ctx.author.mention}. This link will expire in 24 hours.")

    @commands.command()
    async def ytmp4(self, ctx, url):
        filename = await self.download_and_convert(ctx, url, 'mp4')
        download_url = await self.get_download_url(filename)
        await ctx.send(f"Conversion complete! You can download the MP4 [here]({download_url}) {ctx.author.mention}. This link will expire in 24 hours.")

    @commands.command()
    @commands.is_owner()
    async def ytcset(self, ctx, hostname, port):
        self.hostname = hostname
        self.port = int(port)
        await ctx.send(f"Web server settings updated. Hostname: {self.hostname}, Port: {self.port}")

    @commands.command()
    async def ytcurl(self, ctx, filename):
        download_url = await self.get_download_url(filename)
        await ctx.send(f"Download URL for {filename}: {download_url} {ctx.author.mention}. This link will expire in 24 hours.")

    @commands.command()
    async def ytcsettings(self, ctx):
        await ctx.send(f"Web server settings - Hostname: {self.hostname}, Port: {self.port}")

    @commands.command()
    @commands.is_owner()
    async def ytstart(self, ctx):
        if not self.is_server_running:
            self.start_server_task = asyncio.create_task(self.start_server())
            await ctx.send("Web server started.")
        else:
            await ctx.send("Web server is already running.")

    @commands.command()
    @commands.is_owner()
    async def ytstop(self, ctx):
        if self.is_server_running:
            await self.stop_server()
            await ctx.send("Web server stopped.")
        else:
            await ctx.send("Web server is not running.")

    async def get_download_url(self, filename):
        if self.is_server_running:
            base_url = f"http://{self.hostname}:{self.port}"
            return f"{base_url}/videos/{filename}"
        else:
            return None

    async def stop_server(self):
        await self.runner.cleanup()
        self.is_server_running = False

    async def remove_file_after_24_hours(self, filename):
        await asyncio.sleep(24 * 60 * 60)  # Sleep for 24 hours
        filepath = Path(self.data_folder) / filename
        if filepath.is_file():
            os.remove(filepath)

def setup(bot):
    cog = ConverterCog(bot)
    bot.add_cog(cog)
    bot.loop.create_task(cog.remove_file_after_24_hours("example.mp4"))  # Replace with the actual default filename
