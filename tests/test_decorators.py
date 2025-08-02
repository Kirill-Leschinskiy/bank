import pytest

from src.decorators import log


@log(filename="mylog.txt")
def successful_function(x, y):
    return x + y


@log(filename="mylog.txt")
def error_function(x, y):
    return x / y


def test_successful_function(capsys):
    result = successful_function(1, 2)
    assert result == 3

    with open("logs/mylog.txt", "r") as log_file:
        log_content = log_file.readlines()
        assert any("successful_function called at" in line for line in log_content)
        assert "successful_function result: 3" in log_content[-1]


def test_error_function(capsys):
    with pytest.raises(ZeroDivisionError):
        error_function(1, 0)

    with open("logs/mylog.txt", "r") as log_file:
        log_content = log_file.readlines()
        assert any("error_function error: ZeroDivisionError" in line for line in log_content)
