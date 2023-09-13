from .message import MessageCog

def setup(bot):
    bot.add_cog(MessageCog(bot))
