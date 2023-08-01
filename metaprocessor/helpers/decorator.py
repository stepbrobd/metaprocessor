import sys
from functools import update_wrapper
from typing import Callable

import click
from rich import print


def metawear(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Callable:
        if sys.platform == "linux":
            return func(*args, **kwargs)
    return wrapper


def linux_only(func: Callable) -> Callable:
    @click.pass_context
    def wrapper(ctx, *args, **kwargs) -> Callable:
        if sys.platform == "linux":
            return ctx.invoke(func, ctx.obj, *args, **kwargs)
        else:
            print(
                "[red]This command is only available on Linux based operating systems.[/red]"
            )
            raise SystemExit(1)
    return update_wrapper(wrapper, func)
