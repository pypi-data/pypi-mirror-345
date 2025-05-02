from collections.abc import Callable
from functools import wraps
from typing import Any, Annotated

import pytest
import typer

from typer_repyt.build_command import build_command, OptDef, ArgDef, ParamDef, DecDef
from typer_repyt.exceptions import BuildCommandError, RepytError

from tests.helpers import check_output, check_help, match_output, match_help


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


def test_reference_static_implementation():
    cli = typer.Typer()

    @cli.command()
    @simple_decorator
    @complex_decorator("jawa", k="ewok")
    def static(  # pyright: ignore[reportUnusedFunction]
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

    check_output(cli, "--dyna2=13", "17", expected_substring="dyna1='default1', dyna2=13")
    check_output(
        cli, "--dyna1=anyd", "--dyna2=13", "etim", expected_substring="dyna1='anyd', dyna2=13, mite1='etim', mite2=None"
    )
    match_output(cli, "etim", expected_pattern="Error.*Missing option '--dyna2'", exit_code=2)
    match_output(cli, "--dyna2=13", expected_pattern="Error.*Missing argument 'MITE1'", exit_code=2)

    match_output(
        cli,
        "--dyna2=13",
        "17",
        expected_pattern=[
            "Start simple decorator",
            "Complex decorator args: a='jawa', k='ewok'",
            r"Complex decorator before function call: args=\(\), kwargs={'ctx': .*Context.*, 'mite1': '17', 'dyna2': 13, 'dyna1': 'default1', 'mite2': None}",
            "dyna1='default1', dyna2=13",
            "Complex decorator after function call: result=None",
            "End simple decorator",
        ],
    )

    match_help(
        cli,
        expected_pattern=[
            "Just prints values of passed params",
            r"mite1 TEXT This is mighty argument 1 \[default:None\] \[required\]",
            r"mite2 \[MITE2\] This is mighty argument 2 \[default: None\]",
            r"--dyna2 INTEGER This is dynamic option2 \[default: None\] \[required\]",
            r"--dyna1 TEXT This is dynamic option 1 \[default: default1\]",
        ],
    )


def test_equivalent_dynamic_implementation():
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
        decorators=[
            DecDef(simple_decorator),
            DecDef(complex_decorator, dec_args=["jawa"], dec_kwargs=dict(k="ewok"), is_simple=False),
        ],
        include_context=True,
    )

    check_output(cli, "--dyna2=13", "17", expected_substring="dyna1='default1', dyna2=13")
    check_output(
        cli, "--dyna1=anyd", "--dyna2=13", "etim", expected_substring="dyna1='anyd', dyna2=13, mite1='etim', mite2=None"
    )
    match_output(cli, "etim", expected_pattern="Error.*Missing option '--dyna2'", exit_code=2)
    match_output(cli, "--dyna2=13", expected_pattern="Error.*Missing argument 'MITE1'", exit_code=2)

    match_output(
        cli,
        "--dyna2=13",
        "17",
        expected_pattern=[
            "Start simple decorator",
            "Complex decorator args: a='jawa', k='ewok'",
            r"Complex decorator before function call: args=\(\), kwargs={'ctx': .*Context.*, 'dyna2': 13, 'mite1': '17', 'dyna1': 'default1', 'mite2': None}",
            "dyna1='default1', dyna2=13",
            "Complex decorator after function call: result=None",
            "End simple decorator",
        ],
    )

    match_help(
        cli,
        expected_pattern=[
            "Just prints values of passed params",
            r"mite1 TEXT This is mighty argument 1 \[default:None\] \[required\]",
            r"mite2 \[MITE2\] This is mighty argument 2 \[default: None\]",
            r"--dyna2 INTEGER This is dynamic option2 \[default: None\] \[required\]",
            r"--dyna1 TEXT This is dynamic option 1 \[default: default1\]",
        ],
    )


def test_build_command__option__with_no_help():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str),
    )

    check_output(cli, "--dyna=ZOOM", expected_substring="dyna='ZOOM'")
    match_help(cli, expected_pattern=r"--dyna TEXT \[default: None\] \[required\]")


def test_build_command__option__rich_help_panel():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, rich_help_panel="This is a dynamic option"),
    )

    check_output(cli, "--dyna=ZOOM", expected_substring="dyna='ZOOM'")
    match_help(cli, expected_pattern=r"This is a dynamic option.*--dyna TEXT \[default: None\] \[required\]")


def test_build_command__option__no_show_default():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, default="ZOOM", show_default=False),
    )

    check_output(cli, expected_substring="dyna='ZOOM'")
    match_help(cli, expected_pattern=r"--dyna TEXT(?! \[default)")


def test_build_command__option__prompt__default():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, prompt=True),
    )

    check_output(cli, expected_substring="dyna='ZOOM'", input="ZOOM")
    match_help(cli, expected_pattern=r"--dyna TEXT \[default: None\] \[required\]")


def test_build_command__option__prompt__custom():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, prompt="Gimme an answer"),
    )

    check_output(cli, expected_substring="dyna='ZOOM'", input="ZOOM\n")
    match_help(cli, expected_pattern=r"--dyna TEXT \[default: None\] \[required\]")


# TODO: Figure out how to fix this test
@pytest.mark.skip("Passing input for confirmation prompt is not working")
def test_build_command__option__confirmation_prompt():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, prompt=True, confirmation_prompt=True),
    )

    check_output(cli, expected_substring=["Dyna: ZOOM", "dyna='ZOOM'"], input="ZOOM\nBOOM\n\n\n")
    check_help(cli, expected_pattern=r"--dyna TEXT \[default: None\] \[required\]")


def test_build_command__option__hide_input():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, prompt=True, hide_input=True),
    )

    check_output(cli, expected_substring="dyna='ZOOM'", input="ZOOM\n")
    match_help(cli, expected_pattern=r"--dyna TEXT \[default: None\] \[required\]")


def test_build_command__option__override_name():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, override_name="dyyyna"),
    )

    check_output(cli, "--dyyyna=ZOOM", expected_substring="dyna='ZOOM'")
    match_help(cli, expected_pattern=r"--dyyyna TEXT \[default: None\] \[required\]")


def test_build_command__option__short_name():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, short_name="d"),
    )

    check_output(cli, "-dZOOM", expected_substring="dyna='ZOOM'")

    # TODO: Maybe create an issue for this on typer github? Seems like the options should 1000% be stripped
    # check_output(cli, "-d    ZOOM", expected_substring="dyna='ZOOM'")

    # TODO: figure out what the star in the help output means
    # dyna_pattern = "\* -a TEXT [default: None] [required]"
    match_help(cli, expected_pattern=r"-d TEXT \[default: None\] \[required\]")


def test_build_command__option__callback():
    cli = typer.Typer()

    def back(val: Any):
        print(f"{val=}")
        return val

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, callback=back),
    )

    check_output(cli, "--dyna=ZOOM", expected_substring=["dyna='ZOOM'", "val='ZOOM'"])


def test_build_command__option__is_eager():
    cli = typer.Typer()

    def back1(val: Any):
        print(f"back1: {val=}")
        raise typer.Exit()

    def back2(val: Any):
        print(f"back2: {val=}")
        raise typer.Exit()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str, callback=back1),
        OptDef(name="mite", param_type=str, callback=back2, is_eager=True),
    )

    check_output(cli, "--dyna=ZOOM", "--mite=BOOM", expected_substring="back2: val='BOOM'")


def test_build_command__argument__with_no_help():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str),
    )

    check_output(cli, "BOOM", expected_substring="mite='BOOM'")
    match_help(cli, expected_pattern=r"mite TEXT \[default: None\] \[required\]")


def test_build_command__argument__rich_help_panel():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str, rich_help_panel="This is a mighty argument"),
    )

    check_output(cli, "BOOM", expected_substring="mite='BOOM'")
    match_help(cli, expected_pattern=r"This is a mighty argument.*mite TEXT \[default: None\] \[required\]")


def test_build_command__argument__no_show_default():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str, default="BOOM", show_default=False),
    )

    check_output(cli, expected_substring="mite='BOOM'")
    match_help(cli, expected_pattern=r"mite \[MITE\](?! \[default)")


def test_build_command__argument__metavar():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str, metavar="NITRO"),
    )

    check_output(cli, "BOOM", expected_substring="mite='BOOM'")
    match_help(cli, expected_pattern=r"mite NITRO \[default: None\] \[required\]")


def test_build_command__argument__hidden():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str, hidden=True),
    )

    match_output(cli, expected_pattern="Error.*Missing argument 'MITE'", exit_code=2)
    check_output(cli, "BOOM", expected_substring="mite='BOOM'")
    check_output(cli, "--help", expected_substring=None)


def test_build_command__argument__envvar__single():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str, envvar="MITE"),
    )

    match_output(cli, expected_pattern="Error.*Missing argument 'MITE'", exit_code=2)
    check_output(cli, expected_substring="mite='BOOM'", env_vars=dict(MITE="BOOM"))
    match_help(cli, expected_pattern=r"mite TEXT \[env var: MITE\] \[default: None\] \[required\]")


def test_build_command__argument__envvar__multiple():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str, envvar=["MITE", "NITRO"]),
    )

    match_output(cli, expected_pattern="Error.*Missing argument 'MITE'", exit_code=2)
    check_output(cli, expected_substring="mite='BOOM'", env_vars=dict(MITE="BOOM"))
    check_output(cli, expected_substring="mite='BOOM'", env_vars=dict(NITRO="BOOM"))
    match_help(cli, expected_pattern=r"mite TEXT \[env var: MITE, NITRO\] \[default: None\] \[required\]")


def test_build_command__argument__showenvvar():
    cli = typer.Typer()

    def dynamic(mite: str):
        print(f"{mite=}")

    build_command(
        cli,
        dynamic,
        ArgDef(name="mite", param_type=str, envvar=["MITE"], show_envvar=False),
    )

    check_output(cli, expected_substring="mite='BOOM'", env_vars=dict(MITE="BOOM"))
    match_help(cli, expected_pattern=r"mite TEXT(?! \[env var: MITE\]) \[default: None\] \[required\]")


def test_build_command__decorator__simple():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str),
        decorators=[DecDef(simple_decorator)],
    )

    match_output(
        cli,
        "--dyna=ZOOM",
        expected_pattern=[
            "Start simple decorator",
            "dyna='ZOOM'",
            "End simple decorator",
        ],
    )


def test_build_command__decorator__complex():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str),
        decorators=[DecDef(complex_decorator, dec_args=["jawa"], dec_kwargs=dict(k="ewok"), is_simple=False)],
    )

    match_output(
        cli,
        "--dyna=ZOOM",
        expected_pattern=[
            "Complex decorator args: a='jawa', k='ewok'",
            r"Complex decorator before function call: args=\(\), kwargs={'dyna': 'ZOOM'}",
            "dyna='ZOOM'",
            "Complex decorator after function call: result=None",
        ],
    )


def test_build_command__decorator__multiple():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    build_command(
        cli,
        dynamic,
        OptDef(name="dyna", param_type=str),
        decorators=[
            DecDef(simple_decorator),
            DecDef(complex_decorator, dec_args=["jawa"], dec_kwargs=dict(k="ewok"), is_simple=False),
        ],
    )

    match_output(
        cli,
        "--dyna=ZOOM",
        expected_pattern=[
            "Start simple decorator",
            "Complex decorator args: a='jawa', k='ewok'",
            r"Complex decorator before function call: args=\(\), kwargs={'dyna': 'ZOOM'}",
            "dyna='ZOOM'",
            "Complex decorator after function call: result=None",
            "End simple decorator",
        ],
    )


def test_build_command__decorator__raises_exception_if_args_set_for_simple_decorator():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    with pytest.raises(BuildCommandError, match="Decorator arguments are not allowed for simple decorators"):
        build_command(
            cli,
            dynamic,
            decorators=[
                DecDef(simple_decorator, dec_args=["jawa"], dec_kwargs=dict(k="ewok")),
            ],
        )


def test_build_command__raises_error_on_unsupported_param_def():
    cli = typer.Typer()

    def dynamic(dyna: str):
        print(f"{dyna=}")

    with pytest.raises(RepytError, match="Unsupported parameter definition type"):
        build_command(cli, dynamic, ParamDef(name="mite", param_type=str))
