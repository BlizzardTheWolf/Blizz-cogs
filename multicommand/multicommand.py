import discord
from redbot.core import commands
from copy import copy

class MultiCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content.startswith(";"):
            return
        prefix = (await self.bot.get_valid_prefixes(message.guild))[0]
        raw = message.content[1:]
        for com in raw.split("<>"):
            com = com.strip()
            new_message = copy(message)
            new_message.content = prefix + com
            await self.bot.process_commands(new_message)
