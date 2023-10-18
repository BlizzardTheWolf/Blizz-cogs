import discord
from redbot.core import commands
from discord.ext import tasks
from io import BytesIO

class GetEmote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.reference:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            if replied_message.author == self.bot.user:
                if message.content == ";getemote":
                    await self.send_emotes(replied_message, message.channel)

    async def send_emotes(self, message, channel):
        custom_emojis = [e for e in message.content.split() if e.startswith(":") and e.endswith(":")]
        if custom_emojis:
            embed = discord.Embed(title="Custom Emotes", color=0x7289da)
            for emote in custom_emojis:
                emoji = discord.PartialEmoji.from_str(emote)
                emote_url = None

                if emoji.is_custom_emoji():
                    ext = "gif" if emoji.animated else "png"
                    emote_url = f"https://cdn.discordapp.com/emojis/{emoji.id}.{ext}?v=1"

                if emote_url:
                    embed.add_field(name=emote, value=emote_url)

            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(GetEmote(bot))
