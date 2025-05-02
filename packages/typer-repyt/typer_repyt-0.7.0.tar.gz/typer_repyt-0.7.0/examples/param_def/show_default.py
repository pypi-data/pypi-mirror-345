from typing import Annotated

from typer import Typer, Option
from typer_repyt import build_command, OptDef

cli = Typer()

@cli.command()
def static(
    dyna1: Annotated[str, Option(show_default=False)] = "BOOM",
    dyna2: Annotated[str, Option(show_default="-hidden-")] = "BOOM",
):
    print(f"{dyna1=}, {dyna2=}")


def dynamic(dyna1: str, dyna2: str):
    print(f"{dyna1=}, {dyna2=}")


build_command(
    cli,
    dynamic,
    OptDef(name="dyna1", param_type=str, default="BOOM", show_default=False),
    OptDef(name="dyna2", param_type=str, default="BOOM", show_default="-hidden-"),
)


if __name__ == "__main__":
    cli()
