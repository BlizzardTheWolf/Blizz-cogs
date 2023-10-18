import discord
from redbot.core import commands

class GetEmote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getemote(self, ctx):
        # Check if the message has any custom emojis
        if ctx.message and ctx.message.content:
            custom_emojis = [
                emoji for emoji in ctx.message.guild.emojis if emoji.is_custom_emoji()
            ]

            if custom_emojis:
                embed = discord.Embed(title="Custom Emojis")
                for emoji in custom_emojis:
                    # Add each custom emoji and its image link to the embed
                    embed.add_field(name=emoji.name, value=str(emoji.url))

                await ctx.send(embed=embed)
            else:
                await ctx.send("No custom emojis found in the message.")
        else:
            await ctx.send("No message provided or no custom emojis found.")

def setup(bot):
    bot.add_cog(GetEmote(bot))
