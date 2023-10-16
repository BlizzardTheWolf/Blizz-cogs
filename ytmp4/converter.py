import asyncio
import os
import subprocess
from discord.ext import commands

class YTMP4Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _convert_to_mp4(self, ctx, url):
        await ctx.trigger_typing()  # Show "typing" status while converting

        # Extract the video ID from the URL
        video_id = url.split("v=")[1]

        # Set the default format to mp4
        format_type = "mp4"

        # Check if mp3 is specified in the command
        if format_type == "mp3":
            ffmpeg_command = [
                "ffmpeg", "-i", f"/mnt/converter/{video_id}.mp4", f"/mnt/converter/{video_id}.mp3"
            ]
            try:
                subprocess.run(ffmpeg_command, check=True)
                output_file = f"/mnt/converter/{video_id}.mp3"
            except subprocess.CalledProcessError:
                await ctx.send("An error occurred during conversion.")
                return
        else:
            output_file = f"/mnt/converter/{video_id}.mp4"

        # Return the converted file
        return output_file

    @commands.command()
    async def convert(self, ctx, url, format_type=None):
        if format_type is None:
            format_type = "mp4"

        if format_type not in ["mp4", "mp3"]:
            await ctx.send("Invalid format. Use 'mp4' or 'mp3'.")
            return

        await ctx.trigger_typing()

        if not os.path.exists('/mnt/converter'):
            os.makedirs('/mnt/converter')

        try:
            converted_file = await self._convert_to_mp4(ctx, url)
        except Exception as e:
            await ctx.send(f"An error occurred during video conversion. Error details: {str(e)}")
            return

        await ctx.send("Video conversion complete.")
        await ctx.send(file=discord.File(converted_file))


def setup(bot):
    bot.add_cog(YTMP4Cog(bot))
