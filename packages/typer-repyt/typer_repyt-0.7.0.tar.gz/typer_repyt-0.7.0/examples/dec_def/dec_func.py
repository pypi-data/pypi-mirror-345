from typing import Any
from collections.abc import Callable
from functools import wraps

from typer import Typer
from typer_repyt import build_command, DecDef

def simple_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print("Start simple decorator")
        result = func(*args, **kwargs)
        print("End simple decorator")
        return result
    return wrapper

cli = Typer()

@cli.command()
@simple_decorator
def static():
    print("In command")


def dynamic():
    print("In command")

build_command(
    cli,
    dynamic,
    decorators=[DecDef(dec_func=simple_decorator)],
)


if __name__ == "__main__":
    cli()
