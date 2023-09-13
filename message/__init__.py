from .message import MessageCog

def setup(bot):
    cog = MessageCog(bot)
    bot.add_cog(cog)
