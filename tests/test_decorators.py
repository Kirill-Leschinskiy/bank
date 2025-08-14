import pytest

from src.decorators import log


@log(filename="mylog.txt")
def summary(x, y):
    return x + y


@log(filename="mylog.txt")
def division(x, y):
    return x / y


def test_summary(capsys):
    result = summary(1, 2)
    assert result == 3

    with open("logs/mylog.txt", "r") as log_file:
        log_content = log_file.readlines()
        assert any("summary called at" in line for line in log_content)
        assert "summary result: 3" in log_content[-1]


def test_division(capsys):
    with pytest.raises(ZeroDivisionError):
        division(1, 0)

    with open("logs/mylog.txt", "r") as log_file:
        log_content = log_file.readlines()
        assert any("division error: ZeroDivisionError" in line for line in log_content)
