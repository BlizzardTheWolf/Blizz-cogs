from .moderationcog import ModerationCog, setup

__red_end_user_data_statement__ = (
    "This cog processes message content locally (via a local AI model) to detect "
    "policy-violating content. Flagged message content and author IDs may be posted "
    "to a staff-configured report channel. No data is sent to external services."
)


async def setup(bot):
    from .moderationcog import setup as _setup
    await _setup(bot)

