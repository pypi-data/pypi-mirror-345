# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-w", "--week"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option, "42")

    assert "2024_week_42_RdYlGn_r_heatmap_" in ret.stderr
    assert "week=42" in ret.stderr


def test_last_week_of_the_year(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", "-w", "52")

    assert "2024_RdYlGn_r_heatmap_" in ret.stderr
    assert "week=52" in ret.stderr
