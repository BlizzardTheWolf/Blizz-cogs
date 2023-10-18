import discord
from discord.ext import commands

class EmojiExtractorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getemote(self, ctx):
        custom_emojis = [str(emoji) for emoji in ctx.message.content.split() if emoji.startswith(":") and emoji.endswith(":")]
        if custom_emojis:
            response = "Found custom emojis in the message. Use ;getemote to see them."
            await ctx.send(response)
        else:
            response = "No custom emojis found in the message."
            await ctx.send(response)

def setup(bot):
    bot.add_cog(EmojiExtractorCog(bot))
