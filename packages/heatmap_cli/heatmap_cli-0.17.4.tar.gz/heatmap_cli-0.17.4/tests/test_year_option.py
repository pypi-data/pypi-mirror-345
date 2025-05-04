# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-y", "--year"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option, "2023")
    assert "year=2023" in ret.stderr


def test_raise_exception_no_data_from_csv(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-y", "2099")
    assert "error: no data extracted from csv file" in ret.stderr
