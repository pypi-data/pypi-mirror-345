# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-c", "--cmap"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option, "autumn")
    assert "cmap=['autumn']" in ret.stderr


def test_default_cmap(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D")
    assert "cmap=['RdYlGn_r']" in ret.stderr


@pytest.mark.parametrize("option", ["-c", "--cmap"])
def test_multiple_cmaps(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option, "autumn", option, "RdYlGn_r")
    assert "cmap=['autumn', 'RdYlGn_r']" in ret.stderr
