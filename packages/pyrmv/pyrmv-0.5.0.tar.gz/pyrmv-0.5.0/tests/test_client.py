from datetime import datetime, timedelta
from typing import List

import pytest

from pyrmv import Client, enums
from pyrmv.classes import BoardArrival, BoardDeparture, Journey, Message, Stop, Trip


def test_board_arrival(api_client: Client, sample_stop_id: str):
    assert isinstance(
        api_client.board_arrival(id=sample_stop_id, journeys_max=3), BoardArrival
    )


def test_board_departure(api_client: Client, sample_stop_id: str):
    assert isinstance(
        api_client.board_departure(id=sample_stop_id, journeys_max=3), BoardDeparture
    )


def test_him_search(api_client: Client):
    response = api_client.him_search(time_end=datetime.now() + timedelta(days=10))

    if len(response) != 0:
        assert isinstance(response[0], Message)
    else:
        assert isinstance(response, list)


def test_journey_detail(api_client: Client, sample_journey_id: str):
    assert isinstance(
        api_client.journey_detail(
            sample_journey_id,
            real_time_mode=enums.RealTimeMode.FULL,
        ),
        Journey,
    )


def test_stop_by_coords(api_client: Client, sample_origin: List[str]):
    assert isinstance(
        api_client.stop_by_coords(sample_origin[0], sample_origin[1], max_number=3)[0], Stop
    )


def test_stop_by_id(api_client: Client, sample_stop_id: str):
    assert isinstance(api_client.stop_by_id(sample_stop_id), Stop)


def test_trip_find(
    api_client: Client, sample_origin: List[str], sample_destination: List[float]
):
    assert isinstance(
        api_client.trip_find(
            origin_coord_lat=sample_origin[0],
            origin_coord_lon=sample_origin[1],
            destination_coord_lat=sample_destination[0],
            destination_coord_lon=sample_destination[1],
            messages=True,
        )[0],
        Trip,
    )


def test_trip_recon(
    api_client: Client, sample_origin: List[str], sample_destination: List[float]
):
    assert isinstance(
        api_client.trip_recon(
            api_client.trip_find(
                origin_coord_lat=sample_origin[0],
                origin_coord_lon=sample_origin[1],
                destination_coord_lat=sample_destination[0],
                destination_coord_lon=sample_destination[1],
                messages=True,
            )[0],
        )[0],
        Trip,
    )


def test_stop_by_name(api_client: Client):
    assert isinstance(api_client.stop_by_name("Hauptwache", max_number=1)[0], Stop)
