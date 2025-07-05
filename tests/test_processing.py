from datetime import datetime
import pytest

from src.processing import filter_by_state


@pytest.mark.parametrize('data, expected_state', [([{'id': 1, 'state': 'EXECUTED', 'date': datetime(2024,2,9)},
                                                    {'id': 2, 'state': 'CANCELED', 'date': datetime(2024,5,1)},
                                                    {'id': 3, 'state': 'EXECUTED', 'date': datetime(2025,2,3)}], "EXECUTED"),
                                                  ([{'id': 4, 'state': 'EXECUTED', 'date': datetime(2024,2,9)},
                                                    {'id': 5, 'state': 'CANCELED', 'date': datetime(2024,5,1)},
                                                    {'id': 6, 'state': 'CANCELED', 'date': datetime(2025,2,3)}], "CANCELED"),
                                                  ([{'id': 7, 'state': 'CANCELED', 'date': datetime(2024, 2, 9)},
                                                    {'id': 8, 'state': 'CANCELED', 'date': datetime(2024, 5, 1)},
                                                    {'id': 9, 'state': 'CANCELED', 'date': datetime(2025, 2, 3)}],
                                                   "EXECUTED")
                                                  ])
def test_filter_by_state(data, expected_state):
    for operations in filter_by_state(data, expected_state):
        assert operations['state'] == expected_state

@pytest.mark.parametrize('data, expected_sort', [([{'id': 1, 'state': 'EXECUTED', 'date': datetime(2024,2,9)},
                                                    {'id': 2, 'state': 'CANCELED', 'date': datetime(2024,5,1)},
                                                    {'id': 3, 'state': 'EXECUTED', 'date': datetime(2025,2,3)}], True),
                                                  ([{'id': 4, 'state': 'EXECUTED', 'date': datetime(2024,2,9)},
                                                    {'id': 5, 'state': 'CANCELED', 'date': datetime(2024,5,1)},
                                                    {'id': 6, 'state': 'CANCELED', 'date': datetime(2025,2,3)}], False),
                                                  ([{'id': 7, 'state': 'CANCELED', 'date': datetime(2024, 2, 9)},
                                                    {'id': 8, 'state': 'CANCELED', 'date': datetime(2024, 5, 1)},
                                                    {'id': 9, 'state': 'CANCELED', 'date': datetime(2025, 2, 3)}],
                                                   "EXECUTED")
                                                  ])
def test_sort_by_date(data, expected_sort):
    pass