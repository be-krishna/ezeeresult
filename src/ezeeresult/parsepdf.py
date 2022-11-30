import numpy as np
import pandas as pd
import tabula
from rich import print
from rich.progress import (BarColumn, Progress, SpinnerColumn, TextColumn,
                           TimeElapsedColumn)


def pdf_to_df(filename: str) -> pd.DataFrame:
    """"Read file containing seatno, student name, mothers name and prn and create dataframe from parsed data."""

    progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        SpinnerColumn(),
        TimeElapsedColumn()
    )

    master_task = progress.add_task("[cyan] Processing file...", total=4)

    try:
        with progress:
            while not progress.finished:

                # Using tabula read all the pages containing tables and store tables in numpy array
                pdf_pages = tabula.io.read_pdf(filename, pages='all')
                pages_arr = np.array(pdf_pages, dtype=object)

                progress.update(master_task, advance=1,
                                description="[cyan]Reading file...")

                # Convert each table into pandas dataframe
                table_dfs = list(map(lambda x: pd.DataFrame(x), pages_arr))

                progress.update(master_task, advance=1,
                                description="[cyan]Parsing file...")

                # remove '\r' from the parsed tables
                for x in table_dfs:
                    x.replace('\\r', ' ', regex=True, inplace=True)

                progress.update(master_task, advance=1,
                                description="[cyan]Cleaning dataframe...")

                combined_tabels = pd.concat(table_dfs)
                combined_tabels.rename(
                    columns={'Student Name': 'Student'},
                    inplace=True)

                # if the columns of dataframe don't contain required fields, print error and exit
                if not set(['SeatNo', 'Mother', 'Student']).issubset(combined_tabels.columns):
                    print(
                        "[bold red]Tables not found! Try again with correct file.[/bold red]")
                    raise SystemExit()

                progress.update(master_task, advance=1,
                                description="[cyan]Finished!")
    except Exception as e:
        progress.update(master_task, advance=4, description="[red] Error...")
        print("[red bold]Invalid PDF file! Try again with correct file.[/bold red]")
        raise SystemExit()

    return combined_tabels
