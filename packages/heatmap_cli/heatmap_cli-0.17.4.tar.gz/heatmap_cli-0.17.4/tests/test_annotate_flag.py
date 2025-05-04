# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-a", "--annotate"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option)
    assert "annotate=True" in ret.stderr
    assert "_annotated_" in ret.stderr
