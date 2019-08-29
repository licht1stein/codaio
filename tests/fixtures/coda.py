import pytest
from envparse import env

from codaio import Coda


@pytest.fixture(scope="session")
def coda():
    API_KEY = env("CODA_API_KEY", cast=str)
    return Coda(API_KEY)
