"""The bot module, which handles discord interface"""

from os import getenv
import sys
import logging

import discord
from discord.ext import commands

from api.rootme_api import RootMeAPIManager
from api.rate_limiter import RateLimiter
from bot.custom_help_command import RootPythiaHelpCommand
from bot.root_pythia_cogs import RootPythiaCommands
from database import DatabaseManager


CHANNEL_ID = getenv("CHANNEL_ID")
if CHANNEL_ID is not None and CHANNEL_ID.isnumeric():
    CHANNEL_ID = int(CHANNEL_ID)
else:
    logging.warning(
        "CHANNEL_ID environment variable is either not set or not an integer: %s", CHANNEL_ID
    )


def craft_intents():
    """Function that enables necessary intents for the bot"""

    # Disable everything
    intents = discord.Intents.none()
    # enable guild related events
    # More info: https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.guilds
    intents.guilds = True

    # Warning: message_content is a privileged intents
    # you must authorize it in the discord dev portal https://discord.com/developers/applications
    # enbale message_content privilegied intent to enable commands
    # More info below:
    # https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.message_content
    intents.message_content = True

    # enable guild messages related events
    # More info below:
    # https://docs.pycord.dev/en/stable/api/data_classes.html#discord.Intents.guild_messages
    intents.guild_messages = True

    return intents


########### Create bot object #################
_DESCRIPTION = (
    "RootPythia is a Discord bot fetching RootMe API to notify everyone "
    "when a user solves a new challenge!"
)
_PREFIX = "!"
_INTENTS = craft_intents()

BOT = commands.Bot(
        command_prefix=_PREFIX,
        description=_DESCRIPTION,
        intents=_INTENTS,
        help_command=RootPythiaHelpCommand())

# Create Bot own logger, each Cog will also have its own
BOT.logger = logging.getLogger(__name__)


########### Setup bot events response ###############
@BOT.check
def is_my_channel(ctx):
    return ctx.channel.id == CHANNEL_ID


@BOT.event
async def on_ready():
    # is this call secure??
    BOT.logger.debug("channel id: %s", CHANNEL_ID)

    # Create Rate Limiter, API Manager, and Database Manager objects
    rate_limiter = RateLimiter()
    BOT.logger.debug("Successfully created RateLimiter")
    api_manager = RootMeAPIManager(rate_limiter)
    BOT.logger.debug("Successfully created RootMeAPIManager")
    db_manager = DatabaseManager(api_manager)
    BOT.logger.debug("Successfully created DatabaseManager")

    # Fetch main channel and send initialization message
    BOT.channel = await BOT.fetch_channel(CHANNEL_ID)
    await BOT.channel.send("Channel initliazed")

    # Register cogs
    await BOT.add_cog(RootPythiaCommands(BOT, db_manager))


@BOT.event
async def on_error(event, *args, **kwargs):
    if event == "on_ready":
        BOT.logger.exception("Unhandled exception in 'on_ready' event:")
        BOT.logger.critical(
            "Event '%s' failed, please check debug logs, close connection and exit...",
            event,
        )
        await BOT.close()
        sys.exit(1)
    else:
        # maybe this call is too intrusive/verbose...
        await BOT.channel.send(f"{event} event failed, please check logs for more details")

        BOT.logger.exception("Unhandled exception in '%s' event", event)


@BOT.event
async def on_command(ctx):
    """Add logging when a command is triggered by a user"""
    BOT.logger.info("'%s' command triggered by '%s'", ctx.command, ctx.author)
