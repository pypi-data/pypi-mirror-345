import pytest  # noqa: F401

from tests.settings import get_connection

def test_glpi_session():
    assert get_connection()

