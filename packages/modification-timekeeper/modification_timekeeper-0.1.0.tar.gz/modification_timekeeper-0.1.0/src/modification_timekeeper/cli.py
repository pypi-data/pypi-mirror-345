"""Tool for keeping the modified time in front matter up to date."""

from __future__ import annotations

import argparse
from typing import Sequence

from . import __version__, process_file

PROG = __package__

DEFAULT_TOLERANCE = 60


def main(argv: Sequence[str] | None = None) -> int:
    """
    Tool keeping the modified time in front matter up to date.

    Parameters
    ----------
    argv : Sequence[str] | None, optional
        The arguments passed on the command line.

    Returns
    -------
    int
        Exit code for the process: if the modification time was updated,
        this will be 1 to stop a commit as a pre-commit hook.
    """
    parser = argparse.ArgumentParser(
        prog=PROG,
        description='Update the modified field in the front matter of a file.',
    )
    parser.add_argument(
        'file_path',
        type=str,
        nargs='+',
        help='Path to the file to process.',
    )
    parser.add_argument(
        '--version', action='version', version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '--field-name',
        type=str,
        default='last_modified',
        help='Field name to update in front matter.',
    )
    parser.add_argument(
        '--after-key',
        type=str,
        help="Key after which to insert the field if it isn't already in the front matter.",
    )
    parser.add_argument(
        '--tolerance',
        type=int,
        default=DEFAULT_TOLERANCE,
        help=(
            'Tolerance in seconds for updating the modification time (updates happen '
            'when the tolerance is exceeded).'
        ),
    )
    parser.add_argument(
        '--as-utc',
        action='store_true',
        help='Whether to use UTC for modification time.',
    )

    args = vars(parser.parse_args(argv))

    made_changes = 0
    for file_path in args.pop('file_path'):
        made_changes += process_file(file_path, **args)

    return int(made_changes > 0)


if __name__ == '__main__':
    raise SystemExit(main())
