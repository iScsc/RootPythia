import pytest

from data.rootme_api_example_data import auteurs_with_score_zero_example_data

from database import DatabaseManager
from classes import User


@pytest.mark.asyncio
async def test_add_user(mock_database_manager):
    db = mock_database_manager

    # Trigger test
    # the user 0 doesn't exists on Root Me, and doesn't correspond to the id of
    # tests/data/rootme_api_example_data
    # so if the API Manager isn't mocked correctly this should raise an error
    ret_user = await db.add_user(0)

    assert ret_user is not None
    assert isinstance(ret_user, User)
    assert ret_user.username == "g0uZ"  # heavily dependant on test data!


@pytest.mark.asyncio
async def test_double_add_user(mock_database_manager, mocker):
    db = mock_database_manager

    # Trigger test
    # the 1 is on purpose the id of "g0uZ" auteur in tests/data/rootme_api_example_data to trigger
    # the double user
    await db.add_user(1)
    ret_value = await db.add_user(1)

    assert ret_value is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "idx, expected",
    [
        (-1, False),
        (1, True),
    ],
)
async def test_has_user(idx, expected, mock_database_manager):
    db = mock_database_manager

    # Trigger test
    await db.add_user(idx)
    ret_value = db.has_user(idx)

    assert ret_value == expected


@pytest.mark.asyncio
async def test_get_user(mock_database_manager):
    db = mock_database_manager

    # Trigger test
    added_user = await db.add_user(1)
    got_user = db.get_user(1)

    assert added_user == got_user


@pytest.mark.asyncio
async def test_add_user_with_empty_position(mock_database_manager):
    # Regression test introduced with https://github.com/iScsc/RootPythia/pull/38
    # the position was always parsed as an int however if the user's score is 0
    # the root me api returns an empty position, causing the bug
    # this test ensures this bug doesn't reappear

    # Create an api manager returning the right data, and the associated db object
    db = mock_database_manager
    db.api_manager.get_user_by_id.return_value = auteurs_with_score_zero_example_data

    # Trigger test
    added_user = await db.add_user(819227)

    assert added_user.score == 0
    assert added_user.nb_solves == 0
    assert added_user.rank == 9999999  # default value, will probably have to be updated
