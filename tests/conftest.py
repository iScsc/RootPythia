import pytest


def pytest_configure():
    pytest.dummy = "dummy global variable"


@pytest.fixture
def dummy_fixture():
    """This fixture is a demo fixture"""
    Obj = "not even an object, simply a concept demo"
    return Obj
