import pytest
import discord.ext.test as dpytest


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


# FIXME: this test is currently disabled because of some weird message Queue not empty at test start
# it seems to have remains of old messages from previous run tests.
# the config_bot fixture is function scoped so this shouldn't be the same instance, the problem probably
# roots deeper in some bad handling of coroutines and task loops but this is just an intuition, I openend #13
# on the repo to track this
@pytest.mark.asyncio
async def NOP_test_getuser_not_found(config_bot):
    ###
    # comments are the same than for test_adduser_command you should check it out
    ###
    bot = config_bot

    await dpytest.message("!getuser 42")

    # the .peek() call is needed to not remove the message from queue in order to verify it twice
    assert dpytest.verify().message().peek().contains().content("42")
    assert dpytest.verify().message().contains().content("isn't in the database")
