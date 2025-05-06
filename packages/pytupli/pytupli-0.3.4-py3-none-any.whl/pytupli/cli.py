from pydantic import BaseModel
from pytupli.storage import TupliAPIClient
from fire import Fire
import tabulate

# Formatting


def pretty_printer(result):
    if result is None:
        return

    # display a list of dicts as a table
    if isinstance(result, (list, tuple)) and (
        all(isinstance(x, dict) for x in result) or all(isinstance(x, BaseModel) for x in result)
    ):
        return tabulate.tabulate(
            [
                {
                    col: cell_format(value)
                    for col, value in (
                        row.items() if isinstance(row, dict) else row.model_dump().items()
                    )
                }
                for row in result
            ],
            headers='keys',
        )

    return (
        '\n' + result + '\n' if isinstance(result, str) else result
    )  # otherwise, let fire handle it


def cell_format(value, decimals=3, bool=('✅', '❌')):
    if value is True:
        return bool[0]
    if value is False:
        return bool[1]
    if isinstance(value, float):
        return '{:.{}f}'.format(value, decimals)
    return value


def main():
    Fire(TupliAPIClient, name='pytupli', serialize=pretty_printer)


if __name__ == '__main__':
    main()
