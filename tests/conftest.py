# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import logging

import pytest
import pytest_asyncio
import discord
from discord.ext import commands
import discord.ext.test as dpytest

from data import auteurs_example_data, challenges_example_data

from bot.root_pythia_cogs import RootPythiaCommands
from bot.root_pythia_cogs import NAME as COG_NAME
from bot.dummy_db_manager import DummyDBManager

# these plugins will be automatically imported by pytest
pytest_plugins = ["pytest_mock", "pytest_asyncio"]


class BotSetupError(Exception):
    pass


def pytest_configure():
    pytest.COG_NAME = COG_NAME


@pytest.fixture
def null_logger():
    null_logger_name = "null_logger"

    def create_null_logger():
        logger = logging.getLogger(null_logger_name)
        logger.handlers = [logging.NullHandler()]
        logger.setLevel(logging.INFO)
        logger.propagate = False  # To not actually log the mock
        return logger

    _logger = logging.getLogger(null_logger_name)
    _logger = _logger if _logger.handlers else create_null_logger()

    yield _logger


# the mocker fixture comes with pytest_mock plugin, see pytest_plugins above
@pytest.fixture
def mock_rootme_api_manager(mocker):
    rootme_api_manager = mocker.AsyncMock()

    rootme_api_manager.get_user_by_id.return_value = auteurs_example_data
    rootme_api_manager.get_challenge_by_id.return_value = challenges_example_data

    yield rootme_api_manager


@pytest.fixture
def mock_dummy_db_manager(mock_rootme_api_manager):
    rootme_api_manager = mock_rootme_api_manager

    db = DummyDBManager(rootme_api_manager)
    yield db


# this pytest_asyncio decorator allows to automatically await async fixture before passing them
# to tests
@pytest_asyncio.fixture
async def config_bot(mock_dummy_db_manager, null_logger):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    _bot = commands.Bot(command_prefix="!", intents=intents)

    _bot.logger = null_logger

    await _bot._async_setup_hook()
    await _bot.add_cog(RootPythiaCommands(_bot, mock_dummy_db_manager))

    dpytest.configure(_bot)

    try:
        _bot.channel = next(_bot.get_all_channels())
    except StopIteration as exc:
        raise BotSetupError("_bot.get_all_channels() seems empty") from exc

    yield _bot

    # empty message queue for future tests see https://github.com/CraftSpider/dpytest/issues/116
    await dpytest.empty_queue()

    # stop cog's loop to avoid an annoying error msg while the test is passing
    _bot.get_cog(COG_NAME).check_new_solves.cancel()
