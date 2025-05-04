# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-O", "--output-dir"])
def test_debug_logs(cli_runner, csv_file, tmpdir, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option, tmpdir, "-w", "42")

    assert f"{tmpdir}/001_2024_week_42_RdYlGn_r_heatmap_" in ret.stderr
