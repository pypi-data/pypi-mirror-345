# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-q", "--quiet"])
def test_no_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, option)
    assert "debug=True" not in ret.stderr
    assert "DEBUG: MainProcess: number of cpu:" not in ret.stderr
    assert "DEBUG: MainProcess: added worker" not in ret.stderr
    assert "generate heatmap:" not in ret.stderr
    assert "child process" not in ret.stderr
    assert "process" not in ret.stderr
