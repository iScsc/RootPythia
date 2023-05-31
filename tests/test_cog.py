import pytest
import discord.ext.test as dpytest


@pytest.mark.asyncio
async def test_add_user_command(config_bot):
    # we use (default) --asyncio-mode=strict so the config_bot coroutine must be awaited "by-hand"
    bot = await config_bot

    # if the API Manager is not rightly mocked this test should fail, on purpose!
    # because the API Manager is mocked to always return data from tests/data/rootme_example_data no matter the id passed
    await dpytest.message("!adduser 42")
    assert dpytest.verify().message().contains().content("g0uZ")
