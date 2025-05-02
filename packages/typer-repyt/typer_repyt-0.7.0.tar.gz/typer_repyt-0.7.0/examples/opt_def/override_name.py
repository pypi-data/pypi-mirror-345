from typing import Annotated

from typer import Typer, Option
from typer_repyt import build_command, OptDef

cli = Typer()

@cli.command()
def static(class_name: Annotated[str, Option("--class")]):
    print(f"class={class_name}")


def dynamic(class_name: str):
    print(f"class={class_name}")


build_command(
    cli,
    dynamic,
    OptDef(name="class_name", param_type=str, override_name="class"),
)


if __name__ == "__main__":
    cli()
