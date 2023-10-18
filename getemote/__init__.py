from .emoji_extractor import EmojiExtractorCog

async def setup(bot):
    await bot.add_cog(EmojiExtractorCog(bot))
