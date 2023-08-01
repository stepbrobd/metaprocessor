import click

from metaprocessor.helpers.completion import generate


@click.group()
def completion() -> None:
    """
    Generate completion for supported shells.
    Run the following command to enable completion for your shell, or add it to your shell's configuration file (modification required):\n
    eval "$(mp|metaprocessor completion bash|zsh|fish)"
    """
    pass


@completion.command()
def bash() -> None:
    """
    Generate bash completion script.
    """
    print(generate("bash"))


@completion.command()
def zsh() -> None:
    """
    Generate zsh completion script.
    """
    print(generate("zsh"))


@completion.command()
def fish() -> None:
    """
    Generate fish completion script.
    """
    print(generate("fish"))
