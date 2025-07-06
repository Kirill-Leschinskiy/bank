from datetime import datetime

import pytest

from src.processing import filter_by_state, sort_by_date


@pytest.mark.parametrize(
    "data, expected_state",
    [
        (
            [
                {"id": 1, "state": "EXECUTED", "date": datetime(2024, 2, 9)},
                {"id": 2, "state": "CANCELED", "date": datetime(2024, 5, 1)},
                {"id": 3, "state": "EXECUTED", "date": datetime(2025, 2, 3)},
            ],
            "EXECUTED",
        ),
        (
            [
                {"id": 4, "state": "EXECUTED", "date": datetime(2024, 2, 9)},
                {"id": 5, "state": "CANCELED", "date": datetime(2024, 5, 1)},
                {"id": 6, "state": "CANCELED", "date": datetime(2025, 2, 3)},
            ],
            "CANCELED",
        ),
        (
            [
                {"id": 7, "state": "CANCELED", "date": datetime(2024, 2, 9)},
                {"id": 8, "state": "CANCELED", "date": datetime(2024, 5, 1)},
                {"id": 9, "state": "CANCELED", "date": datetime(2025, 2, 3)},
            ],
            "EXECUTED",
        ),
    ],
)
def test_filter_by_state(data, expected_state):
    for operations in filter_by_state(data, expected_state):
        assert operations["state"] == expected_state


def test_empty_data_for_filter_by_state(empty_data):
    with pytest.raises(ValueError):
        filter_by_state(empty_data)


@pytest.mark.parametrize(
    "data, expected_descending_sort, expected_dates",
    [
        (
            [
                {"id": 1, "state": "EXECUTED", "date": "2020-01-02T12:01:03.311"},
                {"id": 2, "state": "CANCELED", "date": "2020-01-05T12:00:00.000"},
                {"id": 3, "state": "EXECUTED", "date": "2023-01-03T12:00:00.000"},
            ],
            True,
            ["2023-01-03T12:00:00.000", "2020-01-05T12:00:00.000", "2020-01-02T12:01:03.311"],
        ),
        (
            [
                {"id": 4, "state": "EXECUTED", "date": "2024-02-05T12:00:00.000"},
                {"id": 5, "state": "CANCELED", "date": "2024-01-16T12:10:16.115"},
                {"id": 6, "state": "CANCELED", "date": "2024-02-11T12:09:08.100"},
            ],
            False,
            ["2024-01-16T12:10:16.115", "2024-02-05T12:00:00.000", "2024-02-11T12:09:08.100"],
        ),
        (
            [
                {"id": 7, "state": "CANCELED", "date": "2019-01-01T12:00:00.000"},
                {"id": 8, "state": "CANCELED", "date": "2019-01-01T12:00:00.000"},
                {"id": 9, "state": "CANCELED", "date": "2022-11-08T12:03:05.110"},
            ],
            True,
            ["2022-11-08T12:03:05.110", "2019-01-01T12:00:00.000", "2019-01-01T12:00:00.000"],
        ),
    ],
)
def test_sort_by_date(data, expected_descending_sort, expected_dates):
    result = sort_by_date(data, descending_sort=expected_descending_sort)
    assert [item["date"] for item in result] == expected_dates


def test_empty_data_for_sort_by_date(empty_data):
    with pytest.raises(ValueError):
        sort_by_date(empty_data)
