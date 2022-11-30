import os
import pathlib
import socket
import sys
from collections import deque
from enum import Enum

import requests
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.table import Table


def first_run() -> bool:
    __FOLDER = os.path.join(pathlib.Path.home(), ".ezeeresult")
    if os.path.exists(f"{__FOLDER}/.first"):
        return False
    else:
        with open(f"{__FOLDER}/.first", 'w') as f:
            f.write("Hey! you discovered me!")
        return True


def static_table(rows: list) -> Table:
    """Simple table used to render information of top and bottom performers"""

    table = Table(box=box.SIMPLE, expand=True)
    table.add_column("Rank")
    table.add_column("SeatNo")
    table.add_column("Name")
    table.add_column("Marks")

    for i, row in enumerate(rows, start=1):
        table.add_row(str(i), *row)

    return table


def dynamic_table(rows: deque, columns: list = []):
    """Table having height of terminal and updates new values constantly"""

    layout = Layout()
    console = Console()

    table = Table(box=box.SIMPLE, expand=True)
    row_count = os.get_terminal_size()[1]

    rows = list(rows)
    while row_count >= 0:
        table = Table(box=box.SIMPLE, expand=True)
        for i in columns:
            table.add_column(i)

        for row in rows[-row_count:]:
            table.add_row(*row)

        layout.update(table)
        render_map = layout.render(console, console.options)

        if len(render_map[layout].render[-1]) > 2:
            row_count -= 1
        else:
            break

    return table


class InvalidHTMLFileError(Exception):
    """
    Error class generated when the file is invalid and can't be parsed
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def connectioncheck():
    url = "https://results.unipune.ac.in"
    ip = socket.gethostbyname(socket.gethostname())

    if ip.startswith('127.0'):
        raise SystemExit(
            "Your system has no internet connection! Please try again later.")

    if requests.get(url).status_code != 200:
        raise SystemExit(f"'{url}' not reachable! Please try again later.")


def signal_handler(signal, frame):
    """
    Handles CTRL+C during program execution
    """

    print()
    print("Aborted! Exiting...")
    sys.exit(0)


class Semester(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4

    @classmethod
    def get(cls, sem: str):
        match sem:
            case 'I':
                return cls.FIRST
            case 'II':
                return cls.SECOND
            case 'II':
                return cls.THIRD
            case 'IV':
                return cls.FOURTH
            case _:
                cls.FIRST

    def __str__(self):
        return str(self.value)


SUBJECTS: dict = {
    Semester.FIRST: {
        'JAVA': ['INT', 'EXT'],
        'DSA': ['INT', 'EXT'],
        'OOSE': ['INT', 'EXT'],
        'OSC': ['INT', 'EXT'],
        'NT': ['INT', 'EXT'],
        'OC-I': ['INT', 'EXT'],
        'OC-II': ['INT', 'EXT'],
        'PRAC': ['INT', 'EXT'],
        'MINI': ['INT', 'EXT'],
        'SSKILL': ['INT', 'EXT'],
        'HR-I': ['INT', 'EXT'],
        'ISEC-I': ['INT', 'EXT'],
    },
    Semester.SECOND: {
        'PYTHON': ['INT', 'EXT'],
        'SPM': ['INT', 'EXT'],
        'OT': ['INT', 'EXT'],
        'AIT': ['INT', 'EXT'],
        'ADBMS': ['INT', 'EXT'],
        'OC-III': ['INT', 'EXT'],
        'OC-IV': ['INT', 'EXT'],
        'PRAC': ['INT', 'EXT'],
        'MINI': ['INT', 'EXT'],
        'SSKILL': ['INT', 'EXT'],
        'HR-II': ['INT', 'EXT'],
        'ISEC-II': ['INT']
    },
    Semester.THIRD: {
        'MAD': ['INT', 'EXT'],
        'DWDM': ['INT', 'EXT'],
        'STQA': ['INT', 'EXT'],
        'KRAI': ['INT', 'EXT'],
        'CC': ['INT', 'EXT'],
        'OC-V': ['INT', 'EXT'],
        'OC-VI': ['INT', 'EXT'],
        'PRAC': ['INT', 'EXT'],
        'MINI': ['INT', 'EXT'],
        'SSKILL': ['INT', 'EXT'],
        'ISEC-III': ['INT', 'EXT'],
        'SKD-I': ['INT', 'EXT'],
        'ITC': ['INT', 'EXT'],
    },
    Semester.FOURTH: {
        'DEVOPS': ['INT', 'EXT'],
        'PPM&OB': ['INT', 'EXT'],
        'PROJ': ['INT', 'EXT'],
        'ISEC-IV': ['INT', 'EXT'],
        'SKD-II': ['INT', 'EXT'],
    },
}
