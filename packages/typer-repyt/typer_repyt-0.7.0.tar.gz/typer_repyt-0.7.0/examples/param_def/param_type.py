from typing import Annotated

from typer import Typer, Option
from typer_repyt import build_command, OptDef

cli = Typer()

@cli.command()
def static(dyna: Annotated[int | None, Option()]):
    print(f"{dyna=}")


def dynamic(dyna: int | None):
    print(f"{dyna=}")


build_command(cli, dynamic, OptDef(name="dyna", param_type=int | None))


if __name__ == "__main__":
    cli()
