import os
import pathlib
from collections import deque

import pandas as pd
from playwright.sync_api import sync_playwright
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, MofNCompleteColumn, Progress,
                           SpinnerColumn, TimeElapsedColumn)
from rich.text import Text
from .helpers import dynamic_table

__FOLDER = os.path.join(pathlib.Path.home(), ".ezeeresult", "html")


def __tofile(folder: str, filename: str, content: str):
    """
    Helper function to write content to files. Creates folders if they don't exist
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(f"{folder}/{filename}", 'w') as f:
        f.write(content)


def save_all(data: pd.DataFrame):

    # region rich layout

    progress = Progress(
        "{task.description}",
        BarColumn(),
        SpinnerColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )

    download_progress = progress.add_task(
        "[cyan]Downloading...",
        total=len(data.index)
    )

    # Create a layout and split it into three sections
    layout = Layout("root")
    layout.split(
        Layout(name="top", ratio=5),
        Layout(name="bottom", ratio=1),
    )

    layout['bottom'].split_row(
        Layout(name="bottom-left"),
        Layout(name="bottom-right")
    )

    layout['bottom-left'].update(
        Panel(
            Align.center(progress, vertical="middle"),
            title="Progress",
            border_style="green"
        )
    )

    layout['bottom-right'].update(
        Panel(
            Align.center(
                "[bold green]Downloading...[/bold green]", vertical="middle"),
            title="Status",
            border_style="green",
            title_align="center"
        )
    )

    columns = ["Seat No", "Name", "Status"]
    _, height = os.get_terminal_size()
    rows = deque(maxlen=height-15)

    layout['top'].update(
        Panel(
            dynamic_table(rows, columns),
            title="Saved Files",
            border_style="green",
            padding=1,
        ))

    # endregion

    with sync_playwright() as playwright:

        # Create a browswer instance and goto url
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://results.unipune.ac.in/")

        # Once on page, get the first row having MASTER OF COMPUTER APPLICATIONS (REVISED 2020) as its td.
        # Select the first row from rows, which ensures you are always getting latest results
        page.get_by_role("row", name=r'MASTER OF COMPUTER APPLICATIONS \(REVISED 2020\)').first.get_by_role(
            "button", name="Go for Result").click()

        # rich live view
        with Live(layout, refresh_per_second=4, vertical_overflow="visible") as live:
            for x in data.itertuples():
                # if the file already exists, add it to table, update the progress and loop over
                if os.path.exists(f"{__FOLDER}/{x.SeatNo}.html"):
                    rows.append((str(x.SeatNo), x.Student, "Exists"))
                    layout['top'].update(
                        Panel(
                            dynamic_table(rows, columns),
                            title="Saved Files",
                            border_style="green",
                            padding=1,
                        ))
                    progress.update(download_progress, advance=1)
                    continue

                page.type("#ctl00_ContentPlaceHolder1_txtSeatno",
                          str(x.SeatNo), delay=2)
                page.type("#ctl00_ContentPlaceHolder1_txtMother",
                          str(x.Mother), delay=2)
                page.click("#ctl00_ContentPlaceHolder1_btnSubmit",
                           delay=2)

                page.once("domcontentloaded",
                          lambda y: __tofile(
                              folder=__FOLDER,
                              filename=f'{x.SeatNo}.html',
                              content=y.content()
                          ))

                rows.append((str(x.SeatNo), x.Student, "Downloaded"))

                layout['top'].update(
                    Panel(
                        dynamic_table(rows, columns),
                        title="Saved Files",
                        border_style="green",
                        padding=1,
                    ), )

                progress.advance(download_progress)
                page.fill("#ctl00_ContentPlaceHolder1_txtSeatno", "")
                page.fill("#ctl00_ContentPlaceHolder1_txtMother", "")

            _, _, files = next(os.walk(__FOLDER))
            file_count = len(files)

            txt_top = Text.from_markup(
                f"[bold green]Downloaded {file_count} of {len(data.index)} files.[/bold green]", justify="center"
            )

            # txt_bot = Text.from_markup(
            #     f"[bold green]Pages saved at:[/bold green] [red]{__FOLDER}[/red]", justify="center")

            # txt_grp = Group(txt_top, txt_bot)

            layout['bottom-right'].update(
                Panel(
                    Align.center(
                        txt_top, vertical="middle"),
                    title="Status",
                    border_style="green",
                    title_align="center"
                )
            )

    if not file_count == len(data.index):
        progress.update(download_progress, description="Verifying...")
        save_all(data)
    return f'{pathlib.Path()}/{__FOLDER}'


def save_one(seat_no: str, mother: str, student: str):
    '''Save a page corresponding to info at given url for later parsing'''

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch()
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://results.unipune.ac.in/")

        page.get_by_role("row",
                         name=r'MASTER OF COMPUTER APPLICATIONS \(REVISED 2020\)'
                         ).first.get_by_role("button",
                                             name="Go for Result").click()

        page.type("#ctl00_ContentPlaceHolder1_txtSeatno",
                  str(seat_no), delay=2)
        page.type("#ctl00_ContentPlaceHolder1_txtMother",
                  str(mother), delay=2)
        page.click("#ctl00_ContentPlaceHolder1_btnSubmit",
                   delay=2)

        page.once("domcontentloaded",
                  lambda y: __tofile(
                      folder=__FOLDER,
                      filename=f'{seat_no}.html',
                      content=y.content()
                  ))
