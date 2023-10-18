import discord
from redbot.core import commands
from redbot.core.bot import Red

class GetEmoteCog(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        # Check if the message has custom emojis
        custom_emotes = [
            emote.strip(":") for emote in message.content.split() if emote.startswith(":") and emote.endswith(":")
        ]

        if custom_emotes:
            # Store custom emojis in a dictionary with their respective URLs
            emote_info = {emote: f"https://cdn.discordapp.com/emojis/{emote.id}.png" for emote in custom_emotes}

            # Attach emote information to the message
            message.custom_emotes = emote_info

        await super().on_message(message)

    @commands.command()
    async def getemote(self, ctx: commands.Context):
        if hasattr(ctx.message, "custom_emotes"):
            emote_info = ctx.message.custom_emotes
            embed = discord.Embed(title="Custom Emote Links")
            for emote_name, emote_url in emote_info.items():
                embed.add_field(name=emote_name, value=emote_url, inline=False)
            await ctx.send(embed=embed)

def setup(bot: Red):
    bot.add_cog(GetEmoteCog(bot))
