from typing import Annotated

from typer import Typer, Argument
from typer_repyt import build_command, ArgDef

cli = Typer()


@cli.command()
def static(
    mite1: Annotated[str, Argument(envvar="MITE")],
    mite2: Annotated[str, Argument(envvar=["NITRO", "DYNA", "MITE"])],
):
    print(f"{mite1=}, {mite2=}")


def dynamic(mite1: str, mite2: str):
    print(f"{mite1=}, {mite2=}")


build_command(
    cli,
    dynamic,
    ArgDef(name="mite1", param_type=str, envvar="MITE"),
    ArgDef(name="mite2", param_type=str, envvar=["NITRO", "DYNA", "MITE"]),
)


if __name__ == "__main__":
    cli()
