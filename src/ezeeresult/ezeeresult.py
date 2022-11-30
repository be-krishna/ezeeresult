import signal

import click
from .exportdata import export
from .helpers import connectioncheck, signal_handler
from .parsepdf import pdf_to_df
from .savefile import save_all


@click.command()
@click.option('--file',
              #   default="/home/be-krishna/Practice/Python/pypackage/ezeeresult/ezeeresult/name_list_2020.pdf",
              prompt='PDF file',
              help="File containg name, seatno and mothername of students.")
@click.option('--semester',
              default="I",
              prompt='Select semester',
              type=click.Choice(
                  ['I', 'II', 'III', 'IV'],
                  case_sensitive=False
              ),
              help="Result semester.")
@click.option('--sseat',
              prompt='Start seat no.(0 - starts from top)',
              type=click.types.INT,
              default=0,
              show_default=False,
              help="Starting seat no of the given semester.")
@click.option('--eseat',
              prompt='End seat no.(0 - stops at last)',
              type=click.types.INT,
              default=0,
              show_default=False,
              help="Ending seat no of the given semester.")
@click.option('--outfile',
              prompt=f'Output file name (default: marks-[semsester].xlsx)',
              show_default=False,
              help="Excel file name to which data will be written.")
def main(file: str, semester: str, sseat: int, eseat: int, outfile: str):
    data = pdf_to_df(file)

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

    while True:
        # main entry function
        main()


if __name__ == "__main__":
    run()
