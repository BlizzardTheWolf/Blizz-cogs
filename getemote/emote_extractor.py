from redbot.core import commands
import discord
import aiohttp
from io import BytesIO

class EmojiExtractorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        custom_emojis = [str(emoji) for emoji in message.content.split() if ":" in emoji]

        if custom_emojis:
            await message.channel.send("Found custom emojis in the message. Use ;getemote to see them.")

    @commands.command()
    async def getemote(self, ctx):
        custom_emojis = [str(emoji) for emoji in ctx.message.content.split() if ":" in emoji]

        if custom_emojis:
            emote_links = []

            for custom_emoji in custom_emojis:
                d_emoji = discord.PartialEmoji.from_str(custom_emoji)

                if d_emoji.is_custom_emoji():
                    ext = "gif" if d_emoji.animated else "png"
                    url = f"https://cdn.discordapp.com/emojis/{d_emoji.id}.{ext}?v=1"
                    emote_links.append(url)

            if emote_links:
                embed = discord.Embed(title="Custom Emojis")
                for idx, link in enumerate(emote_links, 1):
                    embed.add_field(name=f"Emoji {idx}", value=link, inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("No custom emojis found in the message.")
        else:
            await ctx.send("No custom emojis found in the message.")

def setup(bot):
    bot.add_cog(EmojiExtractorCog(bot))
