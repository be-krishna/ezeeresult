import os
import pathlib
import time
from collections import deque
from itertools import chain

import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, MofNCompleteColumn, Progress,
                           SpinnerColumn, TimeElapsedColumn)
from rich.text import Text

from .helpers import (SUBJECTS, InvalidHTMLFileError, Semester, dynamic_table,
                      static_table)
from .parsehtml import parse
from .savefile import save_one

__FOLDER = os.path.join(pathlib.Path.home(), ".ezeeresult", "html")


def export(df: pd.DataFrame, sseat: int, eseat: int, semester: str, filename: str):
    """
    Function to export collected values as excel file
    """
    data = None
    if sseat and eseat:
        data = df.query(f'SeatNo >= {sseat} and SeatNo <= {eseat}')
    elif sseat and not eseat:
        data = df.query(f'SeatNo >= {sseat}')
    elif eseat and not sseat:
        data = df.query(f'SeatNo <= {eseat}')
    else:
        data = df

    collected = []
    semester = Semester.get(semester)

    #! rich view start
    progress = Progress(
        "{task.description}",
        BarColumn(),
        SpinnerColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )

    parsing_task = progress.add_task("[cyan]Extracting",
                                     total=len(data.index))

    layout = Layout("root")
    layout.split(Layout(name="top", ratio=5), Layout(name="bottom", ratio=1))

    layout['top'].split_row(
        Layout(name="top-left"),
        Layout(name="top-right")
    )

    layout['top-right'].split_column(
        Layout(name="top-right-top"),
        Layout(name="top-right-bottom"),
    )

    layout['top-right'].update(Panel("...", title="Toppers"))

    layout['bottom'].split_row(
        Layout(name="bottom-left"),
        Layout(name="bottom-right")
    )

    layout['bottom-left'].update(
        Panel(
            Align.center(progress, vertical="middle"),
            title="Progress",
            border_style="green",
            padding=(1),
        ))

    layout['bottom-right'].update(
        Panel(
            Align.center(
                "[bold green]Exporting...[/bold green]", vertical="middle"),
            title="Status",
            border_style="green",
            title_align="center"
        )
    )

    columns = ["Seat No", "Name", "PRN"]

    _, height = os.get_terminal_size()
    rows = deque(maxlen=height-15)
    #! rich view end

    top10 = []
    bot10 = []
    with Live(layout, refresh_per_second=4, vertical_overflow="visible") as live:
        for x in data.itertuples():
            try:

                parsed = parse(f'{__FOLDER}/{x.SeatNo}.html',
                               semester, x.SeatNo, x.Student)
                collected.append(parsed)

                rows.append((str(x.SeatNo), str(x.Student), str(x.PRN)))
                layout['top-left'].update(
                    Panel(
                        dynamic_table(rows, columns),
                        title="Saved Files",
                        border_style="green",
                    ))
                progress.update(parsing_task, advance=1)

            except InvalidHTMLFileError as e:
                itxt = Text.from_markup(
                    f"[bold green]Downloading [red]{x.SeatNo} | {x.Student}...[red] [/bold green]"
                )
                itxt.justify = 'center'

                layout['bottom-right'].update(
                    Panel(itxt, title=e or "Error",
                          border_style='green', )
                )

                save_one(str(x.SeatNo), x.Mother, x.Student)
                parsed = parse(f'{__FOLDER}/{x.SeatNo}.html',
                               semester, x.SeatNo, x.Student)

                collected.append(parsed)

                rows.append((str(x.SeatNo), str(x.Student), str(x.PRN)))

                layout['top-left'].update(
                    Panel(
                        dynamic_table(rows, columns=columns),
                        title="Saved Files",
                        border_style="green",
                    ))
                progress.update(parsing_task, advance=1)

            top10 = _top10s(collected)
            bot10 = _bot10s(collected)
            layout['top-right-top'].update(
                Panel(static_table(top10), title="Top Rankers", border_style="green",
                      )
            )
            layout['top-right-bottom'].update(
                Panel(static_table(bot10), title="Bottom Rankers", border_style="green",
                      )
            )
            time.sleep(0.1)
        collected = pd.DataFrame(collected)

        if not filename:
            filename = f"marks-{semester}.xlsx"
        elif filename == "marks-[semsester].xlsx":
            filename = f"marks-{semester}.xlsx"
        else:
            fname, ext = os.path.splitext(filename)
            if not ext:
                filename = f"{fname}.xlsx"
        file_path = _toexcel(collected, semester, filename)

        layout['bottom-right'].update(
            Panel(
                Align.center(
                    f"[bold green]Exported file: [red]{filename}[red][/bold green]", vertical="middle"),
                title="Exported",
                border_style="green",
                title_align="center"
            )
        )

    return file_path


def _top10s(data: list):
    temp = sorted(data, key=lambda x: x[-1], reverse=True)[:10]
    temp = list(map(lambda x: (str(x[0]), str(x[1]), str(x[-1])), temp))
    return temp


def _bot10s(data: list):
    temp = sorted(data, key=lambda x: x[-1])[:10]
    temp = list(map(lambda x: (str(x[0]), str(x[1]), str(x[-1])), temp))
    return temp


def _toexcel(data: pd.DataFrame, sem: Semester, filename: str):
    """
    Write dataframe to excel file
    """
    wb = Workbook()

    ws = wb.active
    ws.title = f'semester-{sem}'

    subs_dict: dict = SUBJECTS[sem]
    top_row: list = list(subs_dict.keys())
    top_row.insert(0, '')
    top_row.insert(1, '')

    sub_sec: list = list(subs_dict.values())

    next_row: list = list(chain(*sub_sec))
    next_row.append('TOTAL')
    next_row.insert(0, 'SEAT')
    next_row.insert(1, 'NAME')

    for i in range(3, len(top_row)*2, 2):
        top_row.insert(i, '')

    ws.append(top_row)

    for i in range(3, len(top_row), 2):
        ws.merge_cells(start_row=1, start_column=i, end_row=1, end_column=i+1)

    ws.append(next_row)

    for r in dataframe_to_rows(data, index=False, header=False):
        ws.append(r)

    export_path = f"{pathlib.Path.home()}/{filename}"

    wb.save(export_path)

    return export_path
