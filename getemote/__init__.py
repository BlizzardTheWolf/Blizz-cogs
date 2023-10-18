from .emote_extractor import EmoteExtractorCog

async def setup(bot):
    await bot.add_cog(EmoteExtractorCog(bot))
