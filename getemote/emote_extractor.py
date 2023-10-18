import discord
from redbot.core import commands

class EmoteExtractorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getemote(self, ctx):
        message = ctx.message
        if message.reference:
            # Check if the message is a reply
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            emoji_codes = self.extract_emoji_codes(replied_message.content)
        else:
            emoji_codes = self.extract_emoji_codes(message.content)

        if not emoji_codes:
            await ctx.send("No custom emoji found in the message.")
            return

        embed = discord.Embed(title="Custom Emoji Links", color=discord.Color.blurple())
        for emoji_code in emoji_codes:
            emoji_url = discord.Embed.Empty
            for emoji in self.bot.emojis:
                if emoji.name == emoji_code:
                    emoji_url = emoji.url
                    break

            embed.add_field(name=f":{emoji_code}:", value=emoji_url, inline=False)

        await ctx.send(embed=embed)

    def extract_emoji_codes(self, text):
        # Extract custom emoji codes from the text
        import re
        return re.findall(r':[a-zA-Z0-9_]+:', text)

def setup(bot):
    bot.add_cog(EmoteExtractorCog(bot))
