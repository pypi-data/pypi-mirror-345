# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [0-based versioning](https://0ver.org/).

## [Unreleased]

## v0.17.4 (2025-05-04)

- Explain how truncate_rounded_count simplifies large numbers
- Fill missing counts with 0 and ensure count is integer type
- Remove interactive prompt for purging output directory, require `--yes` flag
- Update help message in readme
- Use `.loc` for dataframe filtering to avoid `SettingWithCopyWarning`

## v0.17.3 (2025-04-27)

- Bump deps
- Lower case log error header
- Refactor argument parsing and add validation for end-date and input file.
- Refactor data filtering and structuring for heatmap generation
- Remove unused imports and code format

## v0.17.2 (2025-04-20)

- Allow None as default value for title, cmap_min, and cmap_max options
- Bump deps
- Refactor CLI argument parsing and error handling for clarity.
- Remove `sphinx-copybutton` from Pipfile
- Set default colormap if none provided via CLI arguments
- Use webbrowser to open heatmap file with file URI.

## v0.17.1 (2025-04-13)

- Bump deps
- Group build and publish package commands together
- Left align the colorbar bottom label
- Prompt to publish package in release `nox` job
- Rename the label to nearest hundreds

## v0.17.0 (2025-04-06)

- Add -u or author option
- Build package after bump release
- Build release after release nox job
- Bump deps and `pre-commit` hook
- Fix incorrect git options
- Update help message in readme

## v0.16.10 (2025-03-30)

- Bump deps and `pre-commit` hook
- Commit changes after bump release
- Remove over complicated exception handling
- Use session.log instead of print in `nox` job
- Show bumped version when running the release `nox` job

## v0.16.9 (2025-03-23)

- Add missing typehints
- Bump pre-commit hook for validate-project
- Code format
- Ensure date ranges are calculated using datetime objects
- Use better descriptive variable

## v0.16.8 (2025-03-16)

- Add input validation and error handling for CSV parsing.
- Handle `OSError` when removing output directory in `_refresh_output_dir`.
- Ignore `.aider` files
- Limit max demo heatmap count to 12000
- Remove unused variable `_fig` in `_generate_heatmap` function
- Use `Path.cwd()` instead of `os.getcwd()`

## v0.16.7 (2025-03-09)

- Add comment for `_generate_cmap_help`
- Add missing typehints to `nox` config
- Further refactoring of generating cmap help message
- Refactor cmap help message
- Update help message to readme
- Use google python docs style

## v0.16.6 (2025-03-02)

- Add missing args in docstrings for `_generate_heatmap` function
- Add missing docstring to `_truncate_round_count` function
- Bump pre-commit hook for isort
- Refactor prompting for refresh output dir
- Remove unnecessary function
- Use correct and simpler typehints

## v0.16.5 (2025-02-23)

- Add missing type for `_recreate_output_dir` function
- Bump pre-commit hooks
- Fix incorrect checking for win32 platform
- Fix incorrect variable name in comment
- Log warning on unsupported platform when opening image
- Refactor fixture for cli
- Update help message in readme

## v0.16.4 (2025-02-16)

- Refactor refresh output dir
- Set coverage to multiprocessing mode
- Use Path operator instead of comma for path joining
- Use ast.Constant as ast.Str is deprecated for python 3.8+
- Use lowercase for mpl backend for convention

## v0.16.3 (2025-02-09)

- Bump deps and `pre-commit` hooks
- Code format
- Format help message urls
- Remove debugging codes

## v0.16.2 (2025-02-02)

- Bump deps and `pre-commit` hooks

## v0.16.1 (2025-01-26)

- Bump `pre-commit` hook
- Raise error in duplicated dates
- Update help message in readme

## v0.16.0 (2025-01-19)

- Add single quote to selected default values for consistency
- Purge output folder during regeneration of demo heatmaps
- Revise some flags/options short arguments name

## v0.15.0 (2025-01-13)

- Use iso year and week to fix leap year issue
- Rename `--date` to `--end-date` for clarity
- Update incorrect metavar for `--end-date`

## v0.14.4 (2025-01-05)

- Bump copyright years
- Bump deps and `pre-commit` hooks
- Fix showing week in title for leap year
- Refactor generating title with leap year

## v0.14.3 (2024-12-29)

- Bump `pre-commit` hook
- Group `cmap` help message with arg
- Move all remaining `--demo` flag code to Action class
- Refactor EnvironmentAction to use concise code

## v0.14.2 (2024-12-22)

- Bump deps and add missing `black` deps
- Refactor exception logging handling
- Return early when `--quiet` flag is toggle
- Standardize default value for args help text
- Use major Python versions for `pyenv`
- Use variable to replace items per row

## v0.14.1 (2024-12-15)

- Bump deps
- Refactor generating heatmap in separate class
- Refactor setup logging and default cmap

## v0.14.0 (2024-12-08)

- Add `--no-annotate` and toggle annotation by default
- Bump deps
- Update help message in readme

## v0.13.7 (2024-12-01)

- Add requires-python field to project
- Bump deps
- Fix cannot generate demo heatmap in Python 3.9
- Fix invalid literal for int() with base 10 error
- Update Pipfile to Python 3.9

## v0.13.6 (2024-11-24)

- Drop support for Python 3.8
- Ignore R0903 rule in `pylint`
- Move `--demo` flag options to action class
- Update pypi classifier

## v0.13.5 (2024-11-17)

- Bump deps and `pre-commit` hooks
- Bump deps using minimum supported Python version in `nox`
- Remove duplicate flag in `--demo` flag

## v0.13.4 (2024-11-10)

- Bump deps
- Refactor demo into argparse's action
- Update help message in readme

## v0.13.3 (2024-11-03)

- Bump deps
- Fix incorrect help string
- Update help message in readme

## v0.13.2 (2024-10-27)

- Bump deps and `pre-commit` hooks
- Switch Python version to 3.13.0 to all `nox` tasks

## v0.13.1 (2024-10-20)

- Bump deps and `pre-commit` hooks
- Support Python 3.13.0 in `pyenv` and `nox`
- Remove debug code and code format

## v0.13.0 (2024-10-13)

- Add `-d` or `--date` to generate heatmap until the date of the year
- Bump deps and `pre-commit` hooks
- Replace two characters options with single character alternative
- Support bumping major, minor, and micro version in `release` task in `nox`

## v0.12.26 (2024-10-06)

- Bump deps and Python version in `pyenv`

## v0.12.25 (2024-09-29)

- Bump deps and `pre-commit` hooks
- Use private function to display environment info

## v0.12.24 (2024-09-22)

- Bump Python versions for `pyenv`
- Bump deps

## v0.12.23 (2024-09-15)

- Bump deps
- Refactor showing stacktrace based on raw args

## v0.12.22 (2024-09-08)

- Add `posargs` to most `nox` sessions
- Bump deps
- Update `nox` sessions in contributing doc
- Update comment on how to run specific task in `lint` session

## v0.12.21 (2024-09-01)

- Bump deps and `pre-commit` hooks
- Refactor env flag action

## v0.12.20 (2024-08-25)

- Bump deps and `pyenv` version
- Refactor `release` session in `nox`
- Resolve `pylint` warnings

## v0.12.19 (2024-08-18)

- Bump deps and `pre-commit` hooks
- Run lint session with latest Python
- Truncate updated readme during write
- Update `nox` sessions in contributing doc

## v0.12.18 (2024-08-11)

- Add `release` session in `nox` to bump app version
- Bump deps and `pre-commit` hooks
- Refactor showing environment details as action in `argparse`

## v0.12.17 (2024-08-04)

- Add extra args when running `test` session
- Bump deps and `pre-commit` hooks
- Remove extra empty lines in `nox` config

## v0.12.16 (2024-07-28)

- Bump deps and `pre-commit` hooks
- Refactor `readme` section to correctly update the README file
- Use common helper to install deps

## v0.12.15 (2024-07-21)

- Bump deps
- Fix first line of comment in imperative mood
- Generate doc within venv managed by `nox` in host environment
- Update `nox` sessions in contributing doc

## v0.12.14 (2024-07-14)

- Bump deps
- Do not reuse `venv` in all `nox` sessions
- Refactor `readme` session in `nox`

## v0.12.13 (2024-07-07)

- Update `nox` sessions in contributing doc
- Do not reuse `venv` in all `nox` sessions
- Bump deps and `pyenv` Python versions

## v0.12.12 (2024-06-30)

- Bump deps and `pre-commit` hooks
- Remove `tox` related deps

## v0.12.11 (2024-06-23)

- Add `readme` nox session to update help message in readme
- Bump deps and `pre-commit` hooks
- Set CLI program name explicitly

## v0.12.10 (2024-06-16)

- Bump and add missing deps
- Reuse virtualenv for selected `nox` sessions

## v0.12.9 (2024-06-09)

- Bump deps
- Remove `tox` deps
- Update `nox` session output in contributing doc

## v0.12.8 (2024-06-02)

- Bump deps
- Fix incorrect `nox` session description
- Remove `tox` and switch to `nox`

## v0.12.7 (2024-05-26)

- Add `cov` (coverage) session to `nox`
- Bump deps and `pre-commit` hooks

## v0.12.6 (2024-05-19)

- Add `doc` sessino to `nox`
- Bump deps
- Remove subheaders from changelog

## v0.12.5 (2024-05-12)

- Add `lint` session for `nox`
- Bump deps and `pre-commit` hooks

## v0.12.4 (2024-05-05)

- Bump deps and `pre-commit` hooks
- Update readme and contributing doc

## v0.12.3 (2024-04-28)

- Bump deps and `pre-commit` hooks

## v0.12.2 (2024-04-21)

- Fix deps lock and update deps
- Update incorrect comment
- Validate output image format

## v0.12.1 (2024-04-14)

- Bump deps, `pre-commit` hooks, and Python versions for `pyenv`
- Update help message in README

## v0.12.0 (2024-04-07)

- Add `-f` or `--format` option to set the heatmap image format
- Bump deps
- Update help message in README

## v0.11.6 (2024-03-31)

- Bump deps
- Fix incorrect label when walking steps exceeding 20k
- Update help message in README

## v0.11.5 (2024-03-24)

- Fix newline in the `sys.version` output on Python 3.8
- Test `--env` flag

## v0.11.4 (2024-03-17)

- Add default value for `--env` in help message
- Add program name to colourbar label
- Bump deps and `pre-commit` hooks
- Fix incorrect headers in changelog

## v0.11.3 (2024-03-10)

- Bump `pre-commit` hooks
- Fix missing closing parenthesis in description
- Update help message in README

## v0.11.2 (2024-03-03)

- Adjust the width (aspect) of the colour bar to 60
- Align the heatmap title and domain name to left and right
- Extend the max value of the colorbar with arrow
- Fit annotated value by converting value larger than 100 to `>1`
- Remove unused options to generation heatmap
- Resize the padding between the colour bar and heatmap to 0.10
- Revise the heatmap title correctly
- Set and left align the heatmap title by axis
- Set to current year and last week when generating demo heatmaps

## v0.11.1 (2024-02-25)

- Update help message in README

## v0.11.0 (2024-02-18)

- Add `-o` or `--open` flag to open the generated heatmap using default program

## v0.10.1 (2024-02-11)

- Add missing types in doc
- Remove `creosote` pre-commit hook

## v0.10.0 (2024-02-04)

- Add `-e` or `--env` flag for printing environment details for bug reporting

## v0.9.3 (2024-01-28)

- Add instruction on upgrade
- Fix incorrect return type

## v0.9.2 (2024-01-21)

- Fix incorrect long title option name
- Exclude `__repr__` from test coverage

## v0.9.1 (2024-01-14)

- Add missing markdown markup
- Fix incorrect help message in readme

## v0.9.0 (2024-01-07)

- Add `-cmax` or `--cmap-max` to set maximum value of the colormap range
- Add `-cmin` or `--cmap-min` to set minimum value of the colormap range
- Bump copyright year
- Fix test errors due to current year assertion
- Pre-fill dataframe that start from middle of the year

## v0.8.8 (2023-12-31)

- Add additional `pre-commit` hooks
- Bump Python versions for `pyenv` environment
- Fix test default title error when running the test in week 52
- Replace `.prettierignore` config with `pre-commit` config

## v0.8.7 (2023-12-24)

- Add `creosote` pre-commit hook
- Sort deps in Pipfile
- Support all or latest Python versions for pre-commit hooks

## v0.8.6 (2023-12-17)

- Randomize test cases through `pytest-randomly`

## v0.8.5 (2023-12-10)

- Only log output folder creation message when needed
- Refactor output folder re-creation

## v0.8.4 (2023-12-03)

- Only create `sample.csv` file after refreshing the output folder
- Show purging output folder actions at logging.INFO level
- Update help message in README.md

## v0.8.3 (2023-11-26)

- Allow scriptttest runner to accept keyword args
- Always create the output folder
- Check if output directory path is absolute path
- Do not append absolute output directory path to current working directory
- Enable all `--purge` flag related tests
- Revise the pre-conditions before purging output directory
- Update outdated help message in README

## v0.8.2 (2023-11-19)

- Add Developer's Certificate of Origin (DCO) to contributing doc
- Add `-Y` or `--yes` flag to confirm any prompts

## v0.8.1 (2023-11-12)

- Add additional tests on `--purge` flag
- Fix and update incorrect help message
- Fix incorrect editable installation of itself in default environment
- Prompt before purging output folder

## v0.8.0 (2023-11-05)

- Add `-p` or `--purge` flag to remove generated heatmaps specified by
  `--output-folder` option
- Refactor script_runner cli fixture

## v0.7.1 (2023-10-29)

- Add additional tests for `--title` option
- Bump Python's version for `pyenv`
- Remove extra space on title when week is set to last week (52) of the year
- Use short code for `pylint` disabling rules

## v0.7.0 (2023-10-22)

- Add `-t` or `--title` option to set title for heatmap
- Add missing classifier

## v0.6.0 (2023-10-15)

- Add `-cb` or `--cbar` flag to toggle colourbar
- Fix incorrect output when testing help message
- Show all features (annotation, and colorbar) when generating demo heatmaps

## v0.5.2 (2023-10-13)

- Fix duplicate path of `cov` environment in `tox`
- Fix incorrect coverage omit pattern

## v0.5.1 (2023-10-08)

- Fix total number of heatmap not showing
- Support Python 3.12.0

## v0.5.0 (2023-10-01)

- Add `-a` or `--annotate` flag to add count to each heatmap region
- Add `-q` or `--quiet` flag to suppress logging
- Add `flake8-print` and `flake8-simplify` for `pre-commit` check
- Add `heatmap` as alias to `heatmap_cli`
- Refactor annotated count calculation
- Set annotated font size to 8 to better readability

## v0.4.5 (2023-09-24)

- Add missing `flake8` related deps in dev environment
- Allow to generate number of heatmaps by setting `--demo` option
- Filter log record from subprocess by default (`debug` flag is disabled)
- Shorten the logging message when generating PNG file to fit screen width
- Sort test coverage report by coverage percentage

## v0.4.4 (2023-09-17)

- Fix logging not working in child process by switching pooling method from
  spawn to fork
- Suppress `nargs` incompatible type warning

## v0.4.3 (2023-09-11)

- Fix incorrect log format

## v0.4.2 (2023-09-10)

- Fix logging not using the config from command line flag
- Refactor setting default CSV filename for `--demo` flag
- Use correct `pyenv` wording in contributing doc

## v0.4.1 (2023-09-03)

- Ignore default `output` folder
- Optimize heatmaps generation using pooling
- Prepend sequence number to output PNG filename
- Refactor colormaps initialization
- Use generated sample CSV file upon `--demo` flag
- Show all colormaps in help message upon `-v`, or `--verbose` flag
- Switch `pytest-console-script` to `scripttest` due to failure to capture
  worker logs

## v0.4.0 (2023-08-27)

- Add `-dm` or `--demo` flag to generate all heatmaps by colormap
- Add `-od` or `--output-dir` option to set a default output folder for
  generated heatmaps
- Bump Python versions for `pyenv`
- Changelog url should comes before issue url
- Fix two underscores in PNG filename

## v0.3.2 (2023-08-20)

- Generate multiple heatmaps at once by different colormaps through `-cm`
  option

## v0.3.1 (2023-08-13)

- Add logging for `-wk` related usages
- Fix incorrect changelog URL
- Fix title without proper spacing
- Sort URLs in project config

## v0.3.0 (2023-08-06)

- Add `-cm` or `--cmap` option to set a default colormap
- Add additional default hook for `pre-commit`
- Add missing tests for `-wk` option
- Fix incorrect changelog URL
- Fix incorrect coverage configs
- Rename test files based on the right term

## v0.2.2 (2023-07-30)

- Add changelog URL to help message
- Add missing documentation for functions
- Fix incorrect header level in changelog
- Fix incorrect source module in coverage config file
- Move some coverage configs to `tox.ini` file
- Reset DataFrame index after the last filtering step
- Set title and PNG filename to year only when week is set to 52

## v0.2.1 (2023-07-28)

- Fix incorrect header level in changelog
- Move `coverage` config from `tox` to its own file
- Reset DataFrame index after filtering
- Show verbose log of last date of current week

## v0.2.0 (2023-07-23)

- Add `wk` or `--week` argument to filter CSV data until week of the year
- Add `yr` or `--year` argument to filter CSV data by year
- Add additional pre-commit default checks
- Fix incorrect ignored coverage module
- Group all `sphinx` related deps under the `doc` category
- Show generated PNG filename upon completion
- Standardize `tox` environment names
- Suppress logging from `matplotlib` in `debug` mode

## v0.1.3 (2023-07-16)

- Fix missing `pylint` dependency when running `pre-commit`
- Ignore word when running `codespell` pre-commit hook

## v0.1.2 (2023-07-11)

- Install `heatmap_cli` as editable installation in `pipenv` dev env
- Link to license from contributing doc
- Revise `pyenv` installation with plugins in contributing doc
- Use the same output folder for `sphinx` doc generation

## v0.1.1 (2023-07-09)

- Fix incorrect module name in `pre-commit` hooks
- Fix missing dependencies on `pipx` installation

## v0.1.0 (2023-07-08)

- Initial public release
