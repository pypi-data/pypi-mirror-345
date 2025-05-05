"""Test the CLI."""

import datetime as dt
import subprocess
import sys
from textwrap import dedent

import pytest
import yaml

from modification_timekeeper import cli


@pytest.mark.parametrize(
    (
        'field_name',
        'after_key',
        'tolerance',
        'as_utc',
        'current_modification_time',
        'should_change',
    ),
    [
        ('modified', 'date', 0, False, '2025-05-04T11:27:28.664853-04:00', True),
        ('modified', 'date', 0, False, None, True),
        ('modified', 'publication_date', 0, True, None, True),
        (
            'last_modified',
            'date',
            None,
            False,
            dt.datetime.now().astimezone().isoformat(),
            False,
        ),
        (
            'modification_time',
            'publication_date',
            None,
            True,
            dt.datetime.now().astimezone().isoformat(),
            False,
        ),
        (
            'modification_time',
            'publication_date',
            None,
            False,
            (
                dt.datetime.now().astimezone()
                - dt.timedelta(seconds=cli.DEFAULT_TOLERANCE)
            ).isoformat(),
            True,
        ),
    ],
)
def test_main(
    tmp_path,
    capsys,
    field_name,
    after_key,
    tolerance,
    as_utc,
    current_modification_time,
    should_change,
):
    """Test that cli.main() returns the number of files altered."""
    blank_file = tmp_path / 'blank.md'
    blank_file.touch()

    modified_time = (
        f'{field_name}: "{current_modification_time}"'
        if current_modification_time
        else ''
    )

    filename = tmp_path / 'test.md'
    filename.write_text(
        dedent(
            f"""
            ---
            title: Test
            {after_key}: "2024-09-04T10:55:00.000-04:00"
            {modified_time}
            ---
            Some content.
            """
        )
    )

    cli_args = [
        arg
        for arg in [
            f'--field-name={field_name}',
            f'--after-key={after_key}' if after_key else '',
            f'--tolerance={tolerance}' if tolerance else '',
            '--as-utc' if as_utc else '',
            str(blank_file),
            str(filename),
        ]
        if arg
    ]

    files_changed = cli.main(cli_args)
    assert files_changed > 0 if should_change else files_changed == 0

    file_named_in_output = str(filename) in capsys.readouterr().out.strip()
    assert file_named_in_output is should_change

    contents = filename.read_text()
    front_matter = yaml.safe_load(contents.split('---\n')[1])
    if current_modification_time is None:
        assert front_matter[field_name] is not None
    else:
        assert (
            front_matter[field_name] != current_modification_time
            if should_change
            else current_modification_time
        )

    if should_change and as_utc:
        modified_time = dt.datetime.fromisoformat(front_matter[field_name])
        assert modified_time.tzinfo == dt.timezone.utc

    if after_key:
        keys = list(front_matter.keys())
        assert keys.index(field_name) == keys.index(after_key) + 1


def test_cli_version(capsys):
    """Confirm that --version works."""
    with pytest.raises(SystemExit):
        cli.main(['--version'])
    assert f'{cli.PROG} {cli.__version__}' == capsys.readouterr().out.strip()


def test_main_access_cli():
    """Confirm that CLI can be accessed via python -m."""
    result = subprocess.run(
        [sys.executable, '-m', 'modification_timekeeper.cli', '--version']
    )
    assert result.returncode == 0
