# pylint: disable=C0114,C0116

import datetime

import pytest


@pytest.mark.parametrize("option", ["-t", "--title"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", option, "my title is foobar")
    assert "title='my title is foobar'" in ret.stderr
    assert "my title is foobar" in ret.stderr


def test_default_title(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D")

    week = datetime.datetime.today().strftime("%W")
    title = "Year 2024: Total Daily Walking Steps Through Week"
    if week == "52":
        title = "Year 2024: Total Daily Walking Steps"
    assert title in ret.stderr


def test_default_title_on_last_week_of_the_year(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-D", "-w", "52")
    assert "Year 2024: Total Daily Walking Steps" in ret.stderr
