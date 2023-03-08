import types

import pytest


def pytest_configure():
    pytest.dummy = "dummy global variable"


@pytest.fixture
def demo_fixture():
    """This fixture is a demo fixture"""
    obj = types.SimpleNamespace()
    obj.demo_attr = 2
    return obj
