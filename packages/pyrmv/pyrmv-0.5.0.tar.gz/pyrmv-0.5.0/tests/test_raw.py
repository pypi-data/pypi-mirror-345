import pytest

from pyrmv.raw import stop_by_name


def test_stop_by_name(api_token: str):
    assert isinstance(stop_by_name(api_token, "Hauptwache", maxNo=1), dict)
