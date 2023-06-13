import copy

import pytest
import discord.ext.test as dpytest
from asyncio import sleep as asleep

from pngmaker import NewValidatedChallenge
from data import auteurs_example_data


@pytest.mark.asyncio
async def test_adduser_command(config_bot):
    bot = config_bot

    # if the API Manager is not rightly mocked this test should fail, on purpose!
    # because the API Manager is mocked to always return data from tests/data/rootme_example_data no matter the id passed
    await dpytest.message("!adduser 42")
    assert dpytest.verify().message().contains().content("g0uZ")


@pytest.mark.asyncio
async def test_getuser_command(config_bot):
    ###
    # comments are the same than for test_adduser_command you should check it out
    ###
    bot = config_bot

    await dpytest.message("!adduser 42")
    await dpytest.message("!getuser 1")

    # the .peek() call is needed to not remove the message from queue in order to verify it twice
    assert dpytest.verify().message().peek().contains().content("g0uZ")
    assert dpytest.verify().message().contains().content("Points: 3040")


@pytest.mark.asyncio
async def test_getuser_not_found(config_bot):
    ###
    # comments are the same than for test_adduser_command you should check it out
    ###
    bot = config_bot

    await dpytest.message("!getuser 42")

    # the .peek() call is needed to not remove the message from queue in order to verify it twice
    assert dpytest.verify().message().peek().contains().content("42")
    assert dpytest.verify().message().contains().content("isn't in the database")


# FIXME: this test is disabled because for now dpytest seems not to be able to verify files/images
# or I just don't know how to use it?
@pytest.mark.asyncio
async def NOP_test_check_solves_loop(config_bot, mock_rootme_api_manager, mocker):
    bot = config_bot
    rootme_api_manager = mock_rootme_api_manager

    # changing the check_new_solves loop delay interval to speed up the test
    cog = bot.get_cog(pytest.COG_NAME)
    cog.check_new_solves.change_interval(seconds=0.1)
    # disable the file removing in NewValidatedCHallenge.__exit__
    mocker.patch("pngmaker.NewValidatedChallenge.__exit__")

    # Trigger test
    await dpytest.message("!adduser 1")

    # change auteurs data: fake a new solve from root me API
    user_data = copy.deepcopy(auteurs_example_data)
    user_data["validations"].append({"id_challenge": "-1"})
    rootme_api_manager.get_user_by_id.return_value = user_data

    await asleep(0.15)

    assert dpytest.verify().message().file(NewValidatedChallenge.NEW_SOLVE_PATH)
    assert dpytest.verify().message().attachment(NewValidatedChallenge.NEW_SOLVE_PATH)


@pytest.mark.asyncio
async def test_command_exception_handling(config_bot, mocker):
    bot = config_bot
    # patching this method in particular is arbitrary: the only goal is to raise an exception during a command execution
    # I chose the "getuser" command purely arbitrary and this could be changed in the future
    mocker.patch("bot.dummy_db_manager.DummyDBManager.get_user", side_effect=Exception)

    # Trigger test
    with pytest.raises(Exception):
        await dpytest.message("!getuser 1")

    assert dpytest.verify().message().content("Command failed, please check logs for more details")


@pytest.mark.asyncio
async def test_loop_exception_handling(config_bot, mocker):
    bot = config_bot
    # patching "DummyDBManager.get_userS" here!
    mocker.patch("bot.dummy_db_manager.DummyDBManager.get_users", side_effect=Exception)
    # changing the check_new_solves loop delay interval to speed up the test
    cog = bot.get_cog(pytest.COG_NAME)
    cog.check_new_solves.change_interval(seconds=0.1)

    # Trigger test
    await asleep(0.15)

    assert (
        dpytest.verify()
        .message()
        .content("check_new_solves loop failed, please check logs for more details")
    )
