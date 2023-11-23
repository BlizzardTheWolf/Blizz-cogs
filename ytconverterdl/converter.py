import discord
from discord.ext import commands
import aiohttp
import yt_dlp
import asyncio
from redbot.core import data_manager

class ConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = data_manager.cog_data_path(cog_instance=self)
        self.app = aiohttp.web.Application()
        self.runner = aiohttp.web.AppRunner(self.app)
        self.hostname = None
        self.port = 8080
        asyncio.create_task(self.start_server())

    async def start_server(self):
        await self.bot.wait_until_ready()
        site = aiohttp.web.TCPSite(self.runner, self.hostname, self.port)
        await site.start()

    async def handle_video_request(self, request):
        filename = request.match_info.get('filename', '')
        video_path = f"{self.data_folder}/{filename}"
        if not video_path.endswith(('.mp3', '.mp4')) or not video_path.startswith(self.data_folder):
            raise aiohttp.web.HTTPNotFound()
        
        with open(video_path, 'rb') as f:
            return aiohttp.web.Response(body=f.read(), content_type='audio/mpeg' if video_path.endswith('.mp3') else 'video/mp4')

    async def download_and_convert(self, url, format):
        ydl_opts = {
            'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio/best',
            'outtmpl': f'{self.data_folder}/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

        return filename

    @commands.command()
    async def ytmp3(self, ctx, url):
        filename = await self.download_and_convert(url, 'mp3')
        await ctx.send(f"Conversion complete! You can download the MP3 [here]({await self.get_download_url(filename)})")

    @commands.command()
    async def ytmp4(self, ctx, url):
        filename = await self.download_and_convert(url, 'mp4')
        await ctx.send(f"Conversion complete! You can download the MP4 [here]({await self.get_download_url(filename)})")

    @commands.command()
    @commands.is_owner()
    async def ytcset(self, ctx, hostname, port):
        self.hostname = hostname
        self.port = int(port)
        await ctx.send(f"Web server settings updated. Hostname: {self.hostname}, Port: {self.port}")

    @commands.command()
    async def ytcurl(self, ctx, filename):
        download_url = await self.get_download_url(filename)
        await ctx.send(f"Download URL for {filename}: {download_url}")

    @commands.command()
    async def ytcsettings(self, ctx):
        await ctx.send(f"Web server settings - Hostname: {self.hostname}, Port: {self.port}")

    async def get_download_url(self, filename):
        return f"http://{self.hostname}:{self.port}/videos/{filename}"

def setup(bot):
    bot.add_cog(ConverterCog(bot))
