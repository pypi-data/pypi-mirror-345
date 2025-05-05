"""Tool for keeping the modified time in front matter up to date."""

import datetime as dt
import re
from pathlib import Path

import yaml

__version__ = '0.1.2'


def process_file(
    file_path: str, field_name: str, after_key: str, tolerance: int, as_utc: bool
) -> bool:
    """
    Process a file to update the front matter with the last modified time.

    Parameters
    ----------
    file_path : str
        The file to process.
    field_name : str
        The name of the modification time field in the front matter.
    after_key : str
        The key after which to insert the modification time field if it isn't already in
        the front matter.
    tolerance : int
        The number of seconds difference between the file's last modification time and
        the front matter's modification time to consider it up to date.
    as_utc : bool
        Whether to show the modification time in UTC.

    Returns
    -------
    bool
        Whether the file was modified.
    """
    file = Path(file_path)
    contents = file.read_text()
    try:
        front_matter = yaml.safe_load(contents.split('---\n')[1])
    except yaml.YAMLError as e:
        print(f'Error parsing YAML front matter: {e}')
        return False
    except IndexError:
        print('No front matter found.')
        return False

    last_modified = dt.datetime.fromtimestamp(file.stat().st_mtime).astimezone(
        dt.timezone.utc if as_utc else None
    )

    if (modified_value := front_matter.get(field_name)) is None or abs(
        last_modified - dt.datetime.fromisoformat(modified_value)
    ).total_seconds() > tolerance:
        front_matter[field_name] = last_modified.isoformat()

        print(
            f"Updating '{field_name}' field in front matter of {file} from "
            f'{modified_value} to {front_matter[field_name]}'
        )

        if modified_value is None:
            pattern = f'({after_key}: .*)' if after_key else '(---)'
            replacement = f'\\g<1>\n{field_name}: "{front_matter[field_name]}"'
        else:
            pattern = f'{field_name}: .*'
            replacement = f'{field_name}: "{front_matter[field_name]}"'

        file.write_text(re.sub(pattern, replacement, contents, count=1))
        return True
    return False
