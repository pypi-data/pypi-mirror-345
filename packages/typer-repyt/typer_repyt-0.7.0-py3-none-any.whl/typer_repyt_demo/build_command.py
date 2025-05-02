"""
This set of demos shows the use of the `attach_settings` decorator.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any
import typer
from typer_repyt import build_command, OptDef, ArgDef, DecDef


def demo_1__build_command__basic():
    """
    This function demonstrates the use of the `build_command()` function.
    The `build_command()` function allows you to dynamically build a Typer
    command using an existing function and some parameter definitions.
    """

    cli = typer.Typer()

    def dynamic(dyna1: str, dyna2: int, mite1: str, mite2: int | None):
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
    )

    cli(["BOOM", "--dyna2=13"])


def demo_2__build_command__with_simple_decorator():
    """
    This function demonstrates how to use the `build_command()` function
    with a simple decorator. The decorator used in this demo is a basic
    decorator that would be used like this in non-dynamic context:

    ```python
    @cli.command()
    @simple_decorator
    def static(dyna: str):
        print(f"{dyna=}")
    ```
    """

    cli = typer.Typer()

    def simple_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"Decorator before function call: {args=}, {kwargs=}")
            result = func(*args, **kwargs)
            print(f"Decorator after function call: {result=}")
            return result

        return wrapper

    def dynamic(dyna: str):
        """
        Just prints values of the passed param
        """
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str),
        decorators=[DecDef(dec_func=simple_decorator)],
    )

    cli(["--dyna=ZOOM"])


def demo_3__build_command__with_chained_decorators():
    """
    This function demonstrates how to use the `build_command()` function
    with multiple decorators. The decorators used in this demo are both
    basic. They are called in _reverse_ order of their definition with
    the decorator declared closer to the function being called first.
    The equivalent static definition would look like:

    ```python
    @cli.command()
    @first_decorator
    @second_decorator
    def static(dyna: str):
        print(f"{dyna=}")
    ```
    """

    cli = typer.Typer()

    def first_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print("Start first decorator")
            result = func(*args, **kwargs)
            print("End first decorator")
            return result

        return wrapper

    def second_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print("Start second decorator")
            result = func(*args, **kwargs)
            print("End second decorator")
            return result

        return wrapper

    def dynamic(dyna: str):
        """
        Just prints values of the passed param
        """
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, help="This is a dynamic option", default="default1"),
        decorators=[DecDef(dec_func=first_decorator), DecDef(dec_func=second_decorator)],
    )

    cli(["--dyna=ZOOM"])


def demo_4__build_command__with_complex_decorator():
    """
    This function demonstrates how to use the `build_command()` function
    with a more complex decorator. The decorator used in this demo is takes
    its own `args` and `kwargs`. Here is the static equivalent:

    ```python
    @cli.command()
    @complex_decorator("jawa", k="ewok")
    def static(dyna: str):
        print(f"{dyna=}")
    ```
    """

    cli = typer.Typer()

    def complex_decorator(a: str, k: str = "hutt") -> Callable[..., Any]:
        def _decorate(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                print(f"Decorator args: {a=}, {k=}")
                print(f"Decorator before function call: {args=}, {kwargs=}")
                result = func(*args, **kwargs)
                print(f"Decorator after function call: {result=}")
                return result

            return wrapper

        return _decorate

    def dynamic(dyna: str):
        """
        Just prints values of the passed param
        """
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str),
        decorators=[DecDef(dec_func=complex_decorator, dec_args=["jawa"], dec_kwargs={"k": "ewok"}, is_simple=False)],
    )

    cli(["--help"])
