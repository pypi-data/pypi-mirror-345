from typing import Annotated

from typer import Typer, Argument
from typer_repyt import build_command, ArgDef

cli = Typer()


@cli.command()
def static(mite: Annotated[str, Argument(envvar="MITE", show_envvar=False)]):
    print(f"{mite=}")


def dynamic(mite: str):
    print(f"{mite=}")


build_command(
    cli,
    dynamic,
    ArgDef(name="mite", param_type=str, envvar="MITE", show_envvar=False),
)


if __name__ == "__main__":
    cli()
