from typing import Annotated

from typer import Typer, Option
from typer_repyt import build_command, OptDef

cli = Typer()


def back(dyna: str):
    print(f"Callback operating on {dyna=}")
    return dyna * 3


@cli.command()
def static(dyna: Annotated[str, Option(callback=back)]):
    print(f"{dyna=}")


def dynamic(dyna: str):
    print(f"{dyna=}")


build_command(
    cli,
    dynamic,
    OptDef(name="dyna", param_type=str, callback=back),
)


if __name__ == "__main__":
    cli()
