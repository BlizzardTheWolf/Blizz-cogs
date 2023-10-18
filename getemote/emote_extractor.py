from redbot.core import commands
import discord
import re

class EmoteExtractorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getemote(self, ctx):
        emote_codes = re.findall(r':\w+:', ctx.message.content)
        emote_urls = []

        for emote_code in emote_codes:
            emote_url = self.get_custom_emoji_url(ctx, emote_code)
            if emote_url:
                emote_urls.append(emote_url)

        if emote_urls:
            emote_links = "\n".join(emote_urls)
            await ctx.send(emote_links)
        else:
            await ctx.send("No custom emojis found in the message.")

    def get_custom_emoji_url(self, ctx, emote_code):
        emote_id = re.search(r'\d+', emote_code)
        if emote_id:
            emote_url = f'https://cdn.discordapp.com/emojis/{emote_id.group(0)}.png'
            return emote_url

def setup(bot):
    bot.add_cog(EmoteExtractorCog(bot))
