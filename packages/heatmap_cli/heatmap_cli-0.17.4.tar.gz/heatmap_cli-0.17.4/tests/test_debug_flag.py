# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-D", "--debug"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, option)
    assert "debug=True" in ret.stderr
    assert "DEBUG: MainProcess: number of cpu:" in ret.stderr
    assert "DEBUG: MainProcess: added worker" in ret.stderr
    assert "generate heatmap:" in ret.stderr


def test_no_debug_logs_in_subprocess(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv)
    assert "debug=False" not in ret.stderr
    assert "child process" not in ret.stderr
    assert "process" not in ret.stderr
    assert "generate heatmap:" in ret.stderr
