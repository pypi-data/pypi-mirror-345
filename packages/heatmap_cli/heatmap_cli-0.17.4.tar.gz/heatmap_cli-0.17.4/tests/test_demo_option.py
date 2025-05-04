# pylint: disable=C0114,C0116


def test_debug_logs(cli_runner):
    ret = cli_runner("-D", "--demo", 1)
    assert "demo=1" in ret.stderr
    assert "input_filename='output/sample.csv'" in ret.stderr


def test_total_default_heatmap_count(cli_runner):
    ret = cli_runner("-h")

    assert (
        "generate number of heatmaps by colormaps (default: '178')"
    ) in ret.stdout
