import types

import pytest

from bot.dummy_db_manager import DummyDBManager
from data import auteurs_example_data, challenges_example_data

# these plugins will be automatically imported by pytest
pytest_plugins = ["pytest_mock", "pytest_asyncio"]

def pytest_configure():
    pytest.dummy = "dummy global variable"


@pytest.fixture
def demo_fixture():
    """This fixture is a demo fixture"""
    obj = types.SimpleNamespace()
    obj.demo_attr = 2
    return obj


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
