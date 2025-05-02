# Dynamically Build Typer Commands

The `build_command` function of the `typer-repyt` library allows you to dynamically construct Typer commands based on a
function template and a list of parameter definitions. This feature is particularly useful if you need to build out a
command based on criteria that might not be completely available until run-time.


## Overview

The `build_command` function takes a Typer app instance, a template function, and a series of parameter definitions to
dynamically generate a Typer command. The template function serves as a blueprint, preserving its name and docstring,
while the parameter definitions provide complete specifications for how to build the arguments and options for the
command.


## Usage

Here's an example of how to use the `build_command` feature:

```python {linenums="1"}
--8<-- "examples/dynamic.py"
```

Try running this example with the `--help` flag to see that the command is dynamically constructed :

```
$ python examples/dynamic.py --help

 Usage: dynamic.py [OPTIONS] MITE1 [MITE2]

 Just prints values of passed params

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────╮
│ *    mite1      TEXT     This is mighty argument 1 [default: None] [required]               │
│      mite2      [MITE2]  This is mighty argument 2 [default: None]                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────╮
│ *  --dyna2                     INTEGER  This is dynamic option 2 [default: None] [required] │
│    --dyna1                     TEXT     This is dynamic option 1 [default: default1]        │
│    --install-completion                 Install completion for the current shell.           │
│    --show-completion                    Show completion for the current shell, to copy it   │
│                                         or customize the installation.                      │
│    --help                               Show this message and exit.                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯
```

The dynamically built function is equivalent to the static definition:

```python {linenums="1"}
--8<-- "examples/static.py"
```

## Details

Let's take a closer look at how we can use the `build_command()` function.


### Function signature

The function signature looks like this:

```python {linenums="1"}
--8<-- "src/typer_repyt/build_command.py:87:94"
```

The `cli` argument is the Typer app that you want your command added to.

The `func` argument is a "template" function. The `build_command()` function builds a brand new function, but it borrows
some parts from the template function. Most importantly, it uses the same code body. So, any logic included in the body
of the template function will appear exactly the same in the built command function. The `build_command()` function will
also preserve the name of the function and it's docstring. This is important, because the function name will become the
name of the command that's added to the app just like it would in a static definition of a Typer command.

!!!note "Template function parameters"

    The function parameters defined in the template function will not be preserved in _any way_ in the generated
    function. They are completely stripped away and replaced with the parameters you pass in `param_defs`. However, it
    may be useful to supply parameters to your template function that match the local values that typer will provide
    when it runs the command. This will ensure that type checkers won't gripe about the function. Note that the dynamic
    example above matches the parameters in the template function with the `param_defs` that are dynamically injected.

The `param_defs` variadic arguments describe the `Option` and `Argument` parameters that will be injected into the
constructed command function. Each of the attributes of `ParamDef`, `OptDef`, and `ArgDef` correspond directly to
parameters that you can use to statically define `Options` and `Arguments` to your command.

The `decorators` keyword argument can be used to provide decorators that should be applied to the command. This option
uses the `DecDef` class to describe each decorator that will be applied.

Finally, the `include_context` keyword argument instructs the `build_command` function whether a `typer.Context`
argument should be included as the first positional argument to the constructed command. Note that in order to use a
context, Typer _requires_ that it be the first positional argument and that it is named "ctx".


### `ParamDef`

`ParamDef` is a base class that contains parameters that are shared by both `Option` and `Argument` command parameters.

Here is the signature of `ParamDef`:

```python {linenums="1"}
--8<-- "src/typer_repyt/build_command.py:17:30"
```

Let's dig into what each attribute is used for.


#### `name`

This will be the name of the parameter.

In this example, the two commands `static` and `dynamic` are equivalent:
```python {linenums="1"}
--8<-- "examples/param_def/name.py"
```

Notice that the first parameter to `static` is
`dyna`. When we build the command dynamically, the `name` attribute we pass to `OptDef` becomse the name of the option.

The help text from both commands is identical:

```
$ python examples/param_def/name.py static --help

 Usage: name.py static [OPTIONS]

╭─ Options ───────────────────────────────────────────────────────────────────────────────────╮
│ *  --dyna        TEXT  [default: None] [required]                                           │
│    --help              Show this message and exit.                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯

$ python examples/param_def/name.py dynamic --help

 Usage: name.py dynamic [OPTIONS]

╭─ Options ───────────────────────────────────────────────────────────────────────────────────╮
│ *  --dyna        TEXT  [default: None] [required]                                           │
│    --help              Show this message and exit.                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯
```


#### `param_type`

This is the type hint for the parameter that Typer will use to cast the command input to the appropriate type. It will
also validate the input with this type so that providing "thirteen", for example, to an `int` typed parameter will raise
an error.

Again, in this example, the two commands `static` and `dynamic` are equivalent:

```python {linenums="1"}
--8<-- "examples/param_def/param_type.py"
```

The `param_type` can be any of the types supported by Typer. In this case, we are actually using a `UnionType` expressed
as `int | None` to indicate that the parameter value will either be an integer or `None`.

!!!note "Only basic unions"

    Typer does not currently support _any_ `UnionType`. Instead, it can only use a `UnionType` that is composed of
    composed of two types: one `NoneType` and any other type that is not `NoneType`. See
    [this issue on GitHub](https://github.com/fastapi/typer/issues/461) for more details.

!!!abstract "Further reading"

    - [Typer: CLI Parameter Types](https://typer.tiangolo.com/tutorial/parameter-types/){target="_blank"}
not
#### `default`

This describes the default value that will be assigned to the parameter. The `default` parmeter may be any Typer
supported type or `None`.

Here is another example with equivalent `static` and `dynamic` commands:

```python {linenums="1"}
--8<-- "examples/param_def/param_type.py"
```

You may be wondering about the `Sentinel` type that `default` can use. Sentinels are a bit of an advanced concept, but
in the plainest terms it lets `build_command` tell the difference between `None` being explicitly passed as the default
value and no default parameter being supplied. You can read more about Sentinel values in PEP 661.

!!!abstract "Further reading"

    - [Typer: Required CLI Options](https://typer.tiangolo.com/tutorial/options/required/){target="_blank"}
    - [Typer: CLI Arguments with Default](https://typer.tiangolo.com/tutorial/arguments/default/){target="_blank"}
    - [PEP 661: Sentinel Types](https://peps.python.org/pep-0661/)

#### `help`

This argument provides the text that will describe the parameter's purpose when you run the command with the `--help`
flag. If it is not provided, Typer won't show any description of the parameter.

Here is yet another example with equivalent commands:

```python {linenums="1"}
--8<-- "examples/param_def/help.py"
```

Here is what the produced `--help` output looks like:

```
$ python examples/param_def/help.py dynamic --help

 Usage: help.py dynamic [OPTIONS]

╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ *  --dyna        TEXT  Dyna goes BOOM [default: None] [required]                             │
│    --help              Show this message and exit.                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

!!!abstract "Further reading"

    - [Typer: CLI Options with Help](https://typer.tiangolo.com/tutorial/options/help/){target="_blank"}
    - [Typer: CLI Arguments with Help](https://typer.tiangolo.com/tutorial/arguments/help/){target="_blank"}


#### `rich_help_panel`

Typer allows you to add more eye candy in the `--help` output by putting parameters inside of Rich panels. This doesn't
add any functionality at all, it just changes the appearance of the `--help` output.

Can you believe it, another example of equivalent commands?

```python {linenums="1"}
--8<-- "examples/param_def/rich_help_panel.py"
```

You can see how the `--dyna` option is now wrapped in a fancy Rich panel in the `--help` output:

```
$ python examples/param_def/rich_help_panel.py dynamic --help

 Usage: rich_help_panel.py dynamic [OPTIONS]

╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Dyna goes BOOM ─────────────────────────────────────────────────────────────────────────────╮
│ *  --dyna        TEXT  [default: None] [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

!!!abstract "Further reading"

    - [Typer: CLI Options with Help -- Help with style using Rich](https://typer.tiangolo.com/tutorial/options/help/#help-with-style-using-rich){target="_blank"}
    - [Typer: CLI Arguments with Help -- Help with style using Rich](https://typer.tiangolo.com/tutorial/arguments/help/#help-with-style-using-rich){target="_blank"}
    - [Rich: Panel](https://rich.readthedocs.io/en/stable/panel.html)


#### `show_default`

This parameter controls whether the default value for a parameter is shown in the `--help` text. If it is set to
`False`, no help will be shown as if the `help` parameter was not supplied. If it is set to a string value, then the
default value is replaced with the supplied string (I'm not sure where this would be useful!).

Let's look at the equivalent commands:

```python {linenums="1"}
--8<-- "examples/param_def/show_default.py"
```

And, here is the `--help` output it produces:

```
$ python examples/param_def/show_default.py dynamic --help

 Usage: show_default.py dynamic [OPTIONS]

╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --dyna1        TEXT                                                                          │
│ --dyna2        TEXT  [default: (-hidden-)]                                                   │
│ --help               Show this message and exit.                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

!!!abstract "Further reading"

    - [Typer: CLI Options with Help -- Hide default from help](https://typer.tiangolo.com/tutorial/options/help/#hide-default-from-help){target="_blank"}
    - [Typer: CLI Options with Help -- Custom default string](https://typer.tiangolo.com/tutorial/options/help/#custom-default-string){target="_blank"}
    - [Typer: CLI Arguments with Help -- Help with defaults](https://typer.tiangolo.com/tutorial/arguments/help/#help-with-defaults){target="_blank"}
    - [Typer: CLI Arguments with Help -- Custom default string](https://typer.tiangolo.com/tutorial/arguments/help/#custom-default-string){target="_blank"}


### `OptDef`

`OptDef` is a the derived class that contains all the remaining parameters that can be passed to a Typer `Option`
parameter.

Here is the signature of `OptDef`:

```python {linenums="1"}
--8<-- "src/typer_repyt/build_command.py:33:45"
```

Let's explore how each of these attributes work.


#### `prompt`

Typer allows you to prompt the user for input when you run a command. This is accomplished with the `prompt` parameter.
The value of this parameter can have two different types. If the type is `bool`, then Typer will just use the `name` of
the parameter as the prompt. If the type is `str`, then the provided string will be used as the prompt.

Here are the equivalent commands:

```python {linenums="1"}
--8<-- "examples/opt_def/prompt.py"
```

When we run the command, we are prompted to provide the values:

```
$ python examples/opt_def/prompt.py dynamic
Dyna1: BOOM
Dyna2 goes [POW]:
dyna1='BOOM', dyna2='POW'
```

Notice that since we provided a `default` value for `dyna2`, it is shown in the prompt and then used if the user doesn't
enter their own value.

!!!abstract "Further reading"

    - [Typer: CLI Option Prompt](https://typer.tiangolo.com/tutorial/options/prompt/#cli-option-prompt){target="_blank"}


#### `confirmation_prompt`

Sometimes, you want to make sure that the text that the user provided the first time is correct by asking them to enter
the same entry again. To accomplish this, we can use a `confirmation_prompt`. After entering the first prompted value,
the user will be prompted to enter it again. Only if the values match will the prompt input be accepted. If it does not
match, the user will be asked to complete the prompt (and confirmation) over again.

Again, we have equivalent implementations:

```python {linenums="1"}
--8<-- "examples/opt_def/confirmation_prompt.py"
```

Running the example produces input like this:

```
$ python examples/opt_def/confirmation_prompt.py dynamic
Dyna: BOOM
Repeat for confirmation: BOOM
dyna='BOOM'


$ python examples/opt_def/confirmation_prompt.py dynamic
Dyna: BOOM
Repeat for confirmation: POW
Error: The two entered values do not match.
Dyna:
```

!!!abstract "Further reading"

    - [Typer: Password CLI Option and Confirmation Prompt](https://typer.tiangolo.com/tutorial/options/password/){target="_blank"}


#### `hide_input`

The `confirmation_prompt` parameter is most useful when you use it with the `hide_input` parameter. Such a combination
can be used to request a password from a user and confirm their entry all while hiding what they are typing. This is a
very familiar pattern on web apps and other CLIs, so it's very nice that it's available in Typer as well.

Here are our equivalent implementations:

```python {linenums="1"}
--8<-- "examples/opt_def/hide_input.py"
```

When we run the example, the input provided to the prompt is completely invisible:

```
$ python examples/opt_def/hide_input.py dynamic
Dyna:
Repeat for confirmation:
dyna='BOOM'
```

!!!abstract "Further reading"

    - [Typer: Password CLI Option and Confirmation Prompt -- A Password prompt](https://typer.tiangolo.com/tutorial/options/password/#a-password-prompt){target="_blank"}


#### `override_name`

Typer also provides a mechanism to override the name of the option. There are many situations in which this is helpful,
but it's probably _most_ helpful when you want the `Option` parameter to use a Python keyword that you can't use as a
parameter name.

Consider these equivalent commands:

```python {linenums="1"}
--8<-- "examples/opt_def/override_name.py"
```

Here is the help that this produces:

```
$ python examples/opt_def/override_name.py dynamic --help

 Usage: override_name.py dynamic [OPTIONS]

╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ *  --class        TEXT  [default: None] [required]                                           │
│    --help               Show this message and exit.                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

Notice how using the `override_name` parameter allows us to have a `--class` option in our command even though the
keyword `class` cannot be used as a parameter name in python.

It's also worth pointing out that unlike the Typer native way of providing an alternative name for the option's long
form, the `override_name` parameter does not require you to include the leading dashes as in `--class`.

!!!abstract "Further reading"

    - [Typer: CLI Option Name](https://typer.tiangolo.com/tutorial/options/name/){target="_blank"}


#### `short_name`

We can also provide a short name for the `Option` using the `short_name` parameter. Like the `override_name` parameter,
you don't need to provide the leading dash (as Typer requires).

Here we have the equivalent commands:

```python {linenums="1"}
--8<-- "examples/opt_def/short_name.py"
```

And this produces some friendly help including the option's short form:

```
$ python examples/opt_def/short_name.py dynamic --help

 Usage: short_name.py dynamic [OPTIONS]

╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ *          -d      TEXT  [default: None] [required]                                          │
│    --help                Show this message and exit.                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

Notice here that if you include `short_name` without an accompanying `override_name`, then the command will `only` use
the short-form. This matches Typer's functionality where if you provide only a shot-form option, the long-form option
will not be used.

!!!abstract "Further reading"

    - [Typer: CLI Option Name -- CLI option short names](https://typer.tiangolo.com/tutorial/options/name/#cli-option-short-names){target="_blank"}


#### `callback`

One of the more interesting abilities of Typer `Option` pareameters is the ability to register a callback. A callback is
a function that:

- is called with the value of the parameter that was provided on the command-line
- operates on it
- returns a value that will replace the value it was called with

Let's look at an example:

```python {linenums="1"}
--8<-- "examples/opt_def/callback.py"
```

Now, let's see what happens when we run this command:

```
$ python examples/opt_def/callback.py dynamic --dyna=BOOM
Callback operating on dyna='BOOM'
dyna='BOOMBOOMBOOM'
```

Here, you can see how the callback mutated the value of `dyna`.

Callback functions are often used for validating the parameter. In those cases, the `callback` would raise an exception
if the value didn't match some needed criteria. However, you can do anything you like with the value passed to a
callback.

!!!abstract "Further reading"

    - [Typer: CLI Option Callback and Context](https://typer.tiangolo.com/tutorial/options/callback-and-context/){target="_blank"}


#### `is_eager`

The `is_eager` parameter simply makes a `callback` attached to an `Option` evaluate before other, non-eager callbacks.
The use-cases for eager callbacks aren't obvious, but you may find the need for it at some point.

Here is the equivalent example for `is_eager`:

```python {linenums="1"}
--8<-- "examples/opt_def/is_eager.py"
```

And, running the command produces this:

```
$ python examples/opt_def/is_eager.py dynamic --dyna1=BOOM --dyna2=POW
Callback 2 operating on val='POW'
Callback 1 operating on val='BOOM'
dyna1='one: BOOM', dyna2='two: POW'
```

Here we see that indeed `back2()` that was designated with `is_eager` was called first.

!!!abstract "Further reading"

    - [Typer: Version CLI Option, `is_eager`](https://typer.tiangolo.com/tutorial/options/version/){target="_blank"}


### `ArgDef`

Like `OptDef`, `ArgDef` is derived from the `ParamDef` class. It contains additional parameters that can only be passed
to a Typer `Argument` parameter.

Here is the signature of `ArgDef`:

```python {linenums="1"}
--8<-- "src/typer_repyt/build_command.py:48:57"
```

Here are what each of the attributes do.


#### `metavar`

You may want to use some special text to be a placeholder in the `--help` text that describes the `Argument`. These are
called "Meta Variables". They help you see where the argument parameter needs to be provided in the command.

Have a look at the equivalent implementations in this example:

```python {linenums="1"}
--8<-- "examples/arg_def/metavar.py"
```

To see where the `metavar` comes in, check out the `--help` output:

```
$ python examples/arg_def/metavar.py dynamic --help

 Usage: metavar.py dynamic [OPTIONS] NITRO

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────╮
│ *    mite      NITRO  [default: None] [required]                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

You an see that it's used as a placeholder in the "Usage" string and again in the argument description.

!!!abstract "Further reading"

    - [Typer: CLI Arguments with Help -- Custom help name (metavar)](https://typer.tiangolo.com/tutorial/arguments/help/#custom-help-name-metavar){target="_blank"}


#### `hidden`

Sometimes, the purpose of an `Argument` is _so_ obvious that it's just redundant to include help text for it. In such a
case, you can hide the help text using the `hidden` parameter.

Observe the example:

```python {linenums="1"}
--8<-- "examples/arg_def/hidden.py"
```

Here you can see how the `Argument` does not have a dedicated help section:

```
$ python examples/arg_def/hidden.py dynamic --help

 Usage: hidden.py dynamic [OPTIONS] MITE

╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

!!!abstract "Further reading"

    - [Typer: CLI Arguments with Help -- Hide a CLI argument from the help text](https://typer.tiangolo.com/tutorial/arguments/help/#hide-a-cli-argument-from-the-help-text){target="_blank"}


#### `envvar`

One very cool feature of Typer is the ability to use an environment variable to provide the value for an `Argument` if
one is not provided by the user. Enter the `envvar` parameter. This acts as a default for the argument if no value is
provided by the user and _if_ the enviornment variable is set.

Additionally, it's possible to provide more than one environment variable that can be used to set the value of the
`Argument`. If more than one is provided, then the `Argument` value will be set by the first environment variable in the
list that is defined.

Let's see it in action in an example:

```python {linenums="1"}
--8<-- "examples/arg_def/envvar.py"
```

First, let's have a look at what the `--help` text looks like for this command:

```
$ python examples/arg_def/envvar.py dynamic --help

 Usage: envvar.py dynamic [OPTIONS] MITE1 MITE2

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────╮
│ *    mite1      TEXT  [env var: MITE] [default: None] [required]                             │
│ *    mite2      TEXT  [env var: NITRO, DYNA, MITE] [default: None] [required]                │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

The environment variables that will be used for the argument are displayed in the help text! Very nice.

Now, let's set some environment variables and run the command:

```
MITE=BOOM DYNA=POW python examples/arg_def/envvar.py dynamic
mite1='BOOM', mite2='POW'
```

You can see that for the second `Argument`, it got the value of the first defined environment variable in its list,
which was the value bound to "DYNA".

!!!abstract "Further reading"

    - [Typer: CLI Arguments with Environment Variables](https://typer.tiangolo.com/tutorial/arguments/envvar/){target="_blank"}


#### `show_envvar`

You may not want to reflect the environment variables used by an `Argument` in the help text. If that's the case, just
set the `show_envvar` parameter to `False`.

Here we have our equivalent implementations:

```python {linenums="1"}
--8<-- "examples/arg_def/show_envvar.py"
```

This results in the environment variables not being shown in the `--help` text:

```
$ python examples/arg_def/show_envvar.py dynamic --help

 Usage: show_envvar.py dynamic [OPTIONS] MITE

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────╮
│ *    mite      TEXT  [default: None] [required]                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

!!!abstract "Further reading"

    - [Typer: CLI Arguments with Environment Variables -- Hide an env var from the help text](https://typer.tiangolo.com/tutorial/arguments/envvar/#multiple-environment-variables){target="_blank"}


### `DecDef`

The `DecDef` class is used to define a decorator that should be added to the final built command. This allows you to
use any of the available decorators that need to be applied to the dynamically constructed function but were not applied
to the original "template" funciton.

Here is the signature of `DecDef`:

```python {linenums="1"}
--8<-- "src/typer_repyt/build_command.py:60:84"
```

!!!note "About `decorate()`"

    The `decorate()` function is used by the `build_command()` function to apply the decorator. It wasn't _intentded_ to
    be used directly, but it may work for other purposes. No gurantees are provided!

Here are what each of the attributes do.


#### `dec_func`

This is the decorator function that should be applied to the dynamically constructed command.

Have a look at the equivalent implementations in this example:

```python {linenums="1"}
--8<-- "examples/dec_def/dec_func.py"
```


Let's run both the static and dynamic command from the example and see that the decorator is applied as expected:

```
$ python examples/dec_def/dec_func.py static
Start simple decorator
In command
End simple decorator

$ python examples/dec_def/dec_func.py dynamic
Start simple decorator
In command
End simple decorator
```


#### `dec_args`

The `dec_args` keyword argument provides a list of positional arguments that should be provided to the decorator.

!!!warning "Complex decorators only!"

    The `dec_args` keyword argument can _only_ be used with a "complex" decorator.

    A "simple" decorator is provided without parentheses or any arguments.

    A "complex" decorator is provided with parentheses and may recieve positional and keyword arguments.

Here are two equivalent implementations with positional arguments:

```python {linenums="1"}
--8<-- "examples/dec_def/dec_args.py"
```


Let's check to make sure that the static and dynamic commands produce the same output:

```
$ python examples/dec_def/dec_args.py static
Complex decorator args: a='jawa', b=13
Complex decorator before function call
In command
Complex decorator after function call

$ uv run python examples/dec_def/dec_args.py dynamic
Complex decorator args: a='jawa', b=13
Complex decorator before function call
In command
Complex decorator after function call
```


#### `dec_kwargs`

The `dec_kwargs` keyword argument provides a dictionary of keyword arguments that should be provided to the decorator.

!!!warning "Complex decorators only!"

    The `dec_kwargs` keyword argument can _only_ be used with a "complex" decorator.

Once again, we have equivalent implementations in an example:

```python {linenums="1"}
--8<-- "examples/dec_def/dec_kwargs.py"
```


Let's check to make sure that the static and dynamic commands produce the same output:

```
$ python examples/dec_def/dec_kwargs.py static
Complex decorator kewyord args: a='ewok', b=21
Complex decorator before function call
In command
Complex decorator after function call

$ python examples/dec_def/dec_kwargs.py dynamic
Complex decorator kewyord args: a='ewok', b=21
Complex decorator before function call
In command
Complex decorator after function call
```


#### `is_simple`

The `is_simple` keyword argument is a flag that indicates whether the provided decorator is "simple" or "complex".
Basically, if the decorator is used without parentheses it is a "simple" decorator. If the decorator must include
parentheses and possibly takes positional and keyword arguments, then it is "complex".

!!!note "Not official"

    The adjectives "simple" and "complex" are not used in official Python documentation. However, it's useful in the
    context of the `typer-repyt` package to clearly explain the difference.

See previous examples to see how `is_simple` can be applied for decorators.
