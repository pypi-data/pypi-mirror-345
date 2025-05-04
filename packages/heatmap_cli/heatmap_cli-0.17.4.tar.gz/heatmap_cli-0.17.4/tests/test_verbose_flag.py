# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-v", "--verbose"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option)
    assert "verbose=1" in ret.stderr


def test_verbose_count(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    for count in range(1, 4):
        verbose = "v" * count
        ret = cli_runner(csv, "-D", f"-{verbose}")
        assert f"verbose={count}" in ret.stderr
