# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-p", "--purge"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option)
    assert "purge=True" in ret.stderr


def test_purge_output_folder_if_exists(cli_runner, csv_file, tmpdir):
    csv = csv_file("sample.csv")
    opf = f"{tmpdir}/output"
    _ = cli_runner(csv, "-D", "-O", opf)
    ret = cli_runner(csv, "-D", "-O", opf, "-p", "-Y")
    assert f"purge output folder: {opf}" in ret.stderr


def test_prompt_when_purging_output_folder(cli_runner, csv_file, tmpdir):
    csv = csv_file("sample.csv")
    opf = f"{tmpdir}/output"
    _ = cli_runner(csv, "-D", "-O", opf)

    ret = cli_runner(csv, "-D", "-O", opf, "-p", stdin=b"y")
    assert f"Are you sure to purge output folder: {opf}? [y/N] " in ret.stdout


def test_no_purge_output_folder_if_not_exists(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    output_folder = csv.resolve().parent.joinpath("output")
    ret = cli_runner(csv, "-D", "-p")
    assert f"purge output folder: {output_folder}" not in ret.stderr
