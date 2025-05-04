# pylint: disable=C0114,C0116

import pytest

from heatmap_cli import __version__


@pytest.mark.parametrize("option", ["-e", "--env"])
def test_env_output(cli_runner, option):
    ret = cli_runner(option)
    assert f"heatmap: {__version__}" in ret.stdout
    assert "python: " in ret.stdout
    assert "platform: " in ret.stdout
