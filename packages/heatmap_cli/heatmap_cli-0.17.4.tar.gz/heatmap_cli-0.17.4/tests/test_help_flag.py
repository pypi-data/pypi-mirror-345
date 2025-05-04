# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_help_message(cli_runner, option):
    ret = cli_runner(option)
    assert (
        "A console program that generates yearly calendar heatmap."
        in ret.stdout
    )
