from .case_list import CaseList

async def setup(bot):
    await bot.add_cog(CaseList(bot))
