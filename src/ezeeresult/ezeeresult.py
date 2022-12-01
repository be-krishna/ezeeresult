import signal
import subprocess

import click
from rich.text import Text
from .exportdata import export
from .helpers import connectioncheck, signal_handler, first_run, seat_check, show_panel
from .parsepdf import pdf_to_df
from .savefile import save_all


@click.command()
@click.option(
    "--file",
    prompt=click.style("PDF file", fg="cyan"),
    help="File containg name, seatno and mothername of students.",
)
@click.option(
    "--semester",
    default="I",
    prompt=click.style("Select semester", fg="cyan"),
    type=click.Choice(["I", "II", "III", "IV"], case_sensitive=False),
    help="Result semester.",
)
@click.option(
    "--sseat",
    prompt=click.style("Start seat no.(0 - starts from top)", fg="cyan"),
    type=click.types.INT,
    default=0,
    show_default=False,
    help="Starting seat no of the given semester.",
)
@click.option(
    "--eseat",
    prompt=click.style("End seat no.(0 - stops at last)", fg="cyan"),
    type=click.types.INT,
    default=0,
    show_default=False,
    help="Ending seat no of the given semester.",
)
@click.option(
    "--outfile",
    prompt=click.style("Output file name", fg="cyan"),
    default="marks-[semsester].xlsx",
    show_default=False,
    help="Excel file name to which data will be written.",
)
def main(file: str, semester: str, sseat: int, eseat: int, outfile: str):
    data = pdf_to_df(file)

    # check if seat no are valid
    seat_check(data, sseat, eseat)

    # clear the screen before proceeding
    click.clear()

    # save all html file for rows in data
    _ = save_all(data)

    # wait for user to exit
    click.pause()

    # export marks to excel file
    file_path = export(data, sseat, eseat, semester, outfile)

    # wait for user to exit
    click.pause()

    # launch explorer where file has been stored
    click.launch(file_path, locate=True)


def run():
    # register signal handler to handle abrupt execution
    signal.signal(signal.SIGINT, signal_handler)

    # if the system has no internet, halt execution
    connectioncheck()

    # if this is first run of application, run command 'playwright install'
    if first_run():
        click.echo("Hey! Need to install few things. Hold on...")
        status = subprocess.run(["playwright", "install"])
        if not status.returncode == 0:
            raise SystemExit("Something went wrong! Try running `playwright install`")
        click.clear()

    show_panel()

    while True:
        # main entry function
        main()


if __name__ == "__main__":
    run()
