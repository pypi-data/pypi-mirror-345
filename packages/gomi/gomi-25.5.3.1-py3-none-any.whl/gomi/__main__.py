# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU GPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import pathlib
import sys
from collections.abc import Callable
from urllib.error import URLError

from .common import ANTPError, init
from .consts import NOTE_TYPES_DIR
from .exporter import export_note_type
from .importer import import_note_type
from .overwriter import overwrite_note_type
from .updater import update_note_type


def wrap_errors(fn: Callable):
    try:
        fn()
    except URLError:
        print("Couldn't connect. Make sure Anki is open and AnkiConnect is installed.")
    except ANTPError as ex:
        print(ex)
    except KeyboardInterrupt:
        print("\nAborted.")


def program_name() -> str:
    return os.path.basename(sys.argv[0])


def print_help():
    options = (
        ("import", "Add one of the stored note types to Anki."),
        ("update", "Overwrite a previously imported note type with new data. Fields will not be updated."),
        (
            "overwrite",
            "Overwrite a note type in Anki with new data from a stored note type. Fields will not be updated.",
        ),
        ("export", "Save your note type to disk as a template."),
        ("list", "List models stored in the templates folder."),
        ("-v, --verbose", "Show detailed info when errors occur."),
    )
    print(f"Usage: {program_name()} [OPTIONS]\n\nOptions:")
    col_width = [max(len(word) for word in col) + 2 for col in zip(*options)]
    for row in options:
        print(" " * 4, "".join(col.ljust(col_width[i]) for i, col in enumerate(row)), sep="")


def list_stored_note_types():
    print("\n".join(os.listdir(NOTE_TYPES_DIR)))


def is_correct_cwd():
    return pathlib.Path.cwd().joinpath(".git").is_dir()


def main() -> int:
    if not is_correct_cwd():
        print("Current directory is not a git repository. Run `git init`.")
        return 1

    if len(sys.argv) < 2:
        print("No action provided.")
        print_help()
        return 1

    init()

    action = None
    wrap = True

    for arg in sys.argv[1:]:
        match arg:
            case "export":
                action = export_note_type
            case "import":
                action = import_note_type
            case "update":
                action = update_note_type
            case "overwrite":
                action = overwrite_note_type
            case "list":
                action = list_stored_note_types
            case "-v" | "--verbose":
                wrap = False

    if action and wrap:
        wrap_errors(action)
    elif action:
        action()
    else:
        print("Unknown action.")
        print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
