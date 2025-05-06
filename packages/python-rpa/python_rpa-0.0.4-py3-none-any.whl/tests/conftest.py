"""This module contains the fixtures for the tests."""

import os

import pytest


def pytest_addoption(parser):
    """Add the --password option to the pytest command."""
    parser.addoption("--password", action="store", default="password", help="Set the environment")


@pytest.fixture(scope='session', autouse=True)
def set_environment(pytestconfig):
    """Set the environment variable based on the --env option."""
    password = pytestconfig.getoption("password")
    os.environ["CONFLUENCE_PASSWORD"] = password

    assert os.environ["CONFLUENCE_PASSWORD"] is not None


def _read_file(file_path):
    """파일에서 문자열을 읽어옵니다."""

    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def read_test_resource(file_path:str):
    """테스트 리소스 디렉토리에서 파일을 읽어옵니다."""

    current_dir = os.path.dirname(__file__)

    file_path = os.path.join(current_dir, file_path)

    return _read_file(file_path)
