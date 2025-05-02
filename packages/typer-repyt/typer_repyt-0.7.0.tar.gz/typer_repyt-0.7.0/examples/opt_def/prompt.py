from typing import Annotated

from typer import Typer, Option
from typer_repyt import build_command, OptDef

cli = Typer()

@cli.command()
def static(
    dyna1: Annotated[str, Option(prompt=True)],
    dyna2: Annotated[str, Option(prompt="Dyna2 goes")] = "POW",
):
    print(f"{dyna1=}, {dyna2=}")


def dynamic(dyna1: str, dyna2: str):
    print(f"{dyna1=}, {dyna2=}")


build_command(
    cli,
    dynamic,
    OptDef(name="dyna1", param_type=str, prompt=True),
    OptDef(name="dyna2", param_type=str, prompt="Dyna2 goes", default="POW"),
)


if __name__ == "__main__":
    cli()
