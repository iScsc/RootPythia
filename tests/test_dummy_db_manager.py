import pytest

from classes import User


@pytest.mark.asyncio
async def test_add_user(mock_dummy_db_manager):
    db = mock_dummy_db_manager

    # Trigger test
    # the user 0 doesn't exists on Root Me, and doesn't correspond to the id of 
    # tests/data/rootme_api_example_data
    # so if the API Manager isn't mocked correctly this should raise an error
    ret_user = await db.add_user(0)

    assert ret_user is not None
    assert type(ret_user) == User
    assert ret_user.username == "g0uZ"  # heavily dependant on test data!


@pytest.mark.asyncio
async def test_double_add_user(mock_dummy_db_manager, mocker):
    db = mock_dummy_db_manager

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
async def test_has_user(idx, expected, mock_dummy_db_manager):
    db = mock_dummy_db_manager

    # Trigger test
    await db.add_user(idx)
    ret_value = db.has_user(idx)

    assert ret_value == expected


@pytest.mark.asyncio
async def test_get_user(mock_dummy_db_manager):
    db = mock_dummy_db_manager

    # Trigger test
    added_user = await db.add_user(1)
    got_user = db.get_user(1)

    assert added_user is got_user
