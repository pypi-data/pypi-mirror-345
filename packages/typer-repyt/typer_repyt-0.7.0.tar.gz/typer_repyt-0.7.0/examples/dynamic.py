from typing import Any
from collections.abc import Callable
from functools import wraps

import typer
from typer_repyt import build_command, OptDef, ArgDef, DecDef


def simple_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print("Start simple decorator")
        result = func(*args, **kwargs)
        print("End simple decorator")
        return result
    return wrapper


def complex_decorator(a: str, k: str = "hutt") -> Callable[..., Any]:
    def _decorate(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"Complex decorator args: {a=}, {k=}")
            print(f"Complex decorator before function call: {args=}, {kwargs=}")
            result = func(*args, **kwargs)
            print(f"Complex decorator after function call: {result=}")
            return result
        return wrapper
    return _decorate


cli = typer.Typer()


def dynamic(ctx: typer.Context, dyna1: str, dyna2: int, mite1: str, mite2: int | None):  # pyright: ignore[reportUnusedParameter]
    """
    Just prints values of passed params
    """
    print(f"{dyna1=}, {dyna2=}, {mite1=}, {mite2=}")


build_command(
    cli,
    dynamic,
    OptDef(name="dyna1", param_type=str, help="This is dynamic option 1", default="default1"),
    OptDef(name="dyna2", param_type=int, help="This is dynamic option 2"),
    ArgDef(name="mite1", param_type=str, help="This is mighty argument 1"),
    ArgDef(name="mite2", param_type=int | None, help="This is mighty argument 2", default=None),
    decorators=[
        DecDef(simple_decorator),
        DecDef(complex_decorator, dec_args=["jawa"], dec_kwargs=dict(k="ewok"), is_simple=False),
    ],
    include_context=True,
)

if __name__ == "__main__":
    cli()
