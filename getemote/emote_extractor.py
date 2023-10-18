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
            emoji = self.get_custom_emoji(ctx, emote_code)
            if emoji:
                emote_urls.append(str(emoji.url))

        if emote_urls:
            emote_links = "\n".join(emote_urls)
            embed = discord.Embed(
                title="Custom Emoji Links",
                description=emote_links,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("No custom emojis found in the message.")

    def get_custom_emoji(self, ctx, emote_code):
        emote_id = re.search(r'\d+', emote_code)
        if emote_id:
            emote = discord.utils.get(ctx.guild.emojis, id=int(emote_id.group(0)))
            return emote

def setup(bot):
    bot.add_cog(EmoteExtractorCog(bot))
