import re

import click
import pandas as pd
from bs4 import BeautifulSoup
from .helpers import InvalidHTMLFileError, Semester


def __extract(file: str) -> list:
    """
    Parses the html file and extracts tables containing marks
    """

    soup = None

    try:
        with open(file, 'r') as f:
            contents = f.read()
            soup = BeautifulSoup(contents, 'html.parser')
        table = soup.findAll(lambda tag: tag.name == 'table')
        marks_table = table[1]
        rows = marks_table.findAll(lambda tag: tag.name == 'tr')

        store = list()

        for row in rows:
            store.append(re.findall(r'[\b|\s|\d](\d{1,}|\-|!)[\b]?', str(row)))

    # if the table doesn't exists, then index error is raised
    except IndexError:
        raise InvalidHTMLFileError("File seems to be corrupted!")

    """
    Remove empty list from marks table. 
    First 3 rows are student info, and last 5 rows are statistics of result
    """
    return list(filter(lambda x: len(x) > 0, store[3:-5]))


def __clean(store: list, semester: Semester) -> list:
    """
    Function to extract marks of the semster passed as argument
    """
    local_store = []
    indices = {
        Semester.FIRST: slice(0, 12),
        Semester.SECOND: slice(13, 25),
        Semester.THIRD: slice(26, 39),
        Semester.FOURTH: slice(40, 45)
    }

    try:
        match semester:
            case Semester.FIRST:
                local_store = store[indices.get(semester)]
                local_store[10].append('-')
                local_store[11].append('-')
                return [x[-5:-3] for x in local_store]

            case Semester.SECOND:
                local_store = store[indices.get(semester)]
                local_store[10].append('-')
                local_store[11].append('-')
                return [x[-5:-3] for x in local_store]

            case Semester.THIRD:
                local_store = store[indices.get(semester)]
                local_store[10].append('-')
                local_store[11].append('-')
                local_store[12].append('-')
                return [x[-5:-3] for x in local_store]
            case Semester.FOURTH:
                local_store = store[indices.get(semester)]
                local_store[3].append('-')
                local_store[4].append('-')
                return [x[-5:-3] for x in local_store]
            case _:
                local_store = store
                return local_store
    except IndexError:
        click.clear()
        raise SystemExit(
            f"Semester {semester} not found for the given roll(s)!")


def __convert(store: list, seat_no: int, s_name: str, semester: Semester) -> list:
    """
    Converts and fills the table with 0 and adds sum at end of the lists.
    """
    sem_i_iii = slice(0, 20)
    sem_iv = slice(0, 3)

    df = pd.DataFrame(store)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    marks = df.to_numpy().flatten().tolist()

    if semester == Semester.FOURTH:
        s_marks = sum(marks[sem_iv])
        marks.append(s_marks)
    else:
        s_marks = sum(marks[sem_i_iii])
        marks.append(s_marks)

    marks.insert(0, s_name)
    marks.insert(0, seat_no)

    return marks


def parse(file: str, semester: Semester, seat: int, name: str) -> list:
    return __convert(__clean(__extract(file), semester), seat, name, semester)
