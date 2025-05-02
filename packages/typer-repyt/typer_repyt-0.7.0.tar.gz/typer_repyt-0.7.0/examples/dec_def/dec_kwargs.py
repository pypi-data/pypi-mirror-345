from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from typer_repyt import build_command, DecDef


def complex_decorator(a: str = "jawa", b: int = 13) -> Callable[..., Any]:
    def _decorate(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"Complex decorator keyword args: {a=}, {b=}")
            print("Complex decorator before function call")
            result = func(*args, **kwargs)
            print("Complex decorator after function call")
            return result
        return wrapper
    return _decorate


cli = typer.Typer()


@cli.command()
@complex_decorator(a="ewok", b=21)
def static():
    print("In command")


def dynamic():
    print("In command")

build_command(
    cli,
    dynamic,
    decorators=[DecDef(dec_func=complex_decorator, dec_kwargs=dict(a="ewok", b=21), is_simple=False)],
)


if __name__ == "__main__":
    cli()
