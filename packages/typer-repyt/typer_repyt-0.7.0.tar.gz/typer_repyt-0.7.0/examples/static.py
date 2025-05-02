from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any

import typer


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

@cli.command()
@simple_decorator
@complex_decorator("jawa", k="ewok")
def static(
    ctx: typer.Context,  # pyright: ignore[reportUnusedParameter]
    mite1: Annotated[str, typer.Argument(help="This is mighty argument 1")],
    dyna2: Annotated[int, typer.Option(help="This is dynamic option 2")],
    dyna1: Annotated[str, typer.Option(help="This is dynamic option 1")] = "default1",
    mite2: Annotated[int | None, typer.Argument(help="This is mighty argument 2")] = None,
):
    """
    Just prints values of passed params
    """
    print(f"{dyna1=}, {dyna2=}, {mite1=}, {mite2=}")


if __name__ == "__main__":
    cli()
