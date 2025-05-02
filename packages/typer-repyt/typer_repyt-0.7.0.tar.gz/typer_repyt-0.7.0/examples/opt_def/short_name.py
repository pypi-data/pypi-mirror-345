from typing import Annotated

from typer import Typer, Option
from typer_repyt import build_command, OptDef

cli = Typer()

@cli.command()
def static(dyna: Annotated[str, Option("-d")]):
    print(f"{dyna=}")


def dynamic(dyna: str):
    print(f"{dyna=}")


build_command(
    cli,
    dynamic,
    OptDef(name="dyna", param_type=str, short_name="d"),
)


if __name__ == "__main__":
    cli()
