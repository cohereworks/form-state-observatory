import pytest


def pytest_addoption(parser):
    parser.addoption('--browser', default='chromium', choices=['chromium', 'firefox', 'webkit'])


@pytest.fixture(scope='session')
def browser_name(request):
    return request.config.getoption('--browser')
