from typing import Annotated

from typer import Typer, Option
from typer_repyt import build_command, OptDef

cli = Typer()


def back1(val: str):
    print(f"Callback 1 operating on {val=}")
    return f"one: {val}"

def back2(val: str):
    print(f"Callback 2 operating on {val=}")
    return f"two: {val}"


@cli.command()
def static(
    dyna1: Annotated[str, Option(callback=back1)],
    dyna2: Annotated[str, Option(callback=back2, is_eager=True)],
):
    print(f"{dyna1=}, {dyna2=}")


def dynamic(dyna1: str, dyna2: str):
    print(f"{dyna1=}, {dyna2=}")


build_command(
    cli,
    dynamic,
    OptDef(name="dyna1", param_type=str, callback=back1),
    OptDef(name="dyna2", param_type=str, callback=back2, is_eager=True),
)


if __name__ == "__main__":
    cli()
