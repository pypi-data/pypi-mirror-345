import sys
import logging

import click
import entrypoints


LOG_LEVEL_CODES = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def merge_extensions(click_group):
    """
    Each extension is called with click group for
    ultimate agility while preserving cli context.
    """
    for extension in load_extensions():
        extension(click_group)
    return click_group


def load_extensions():
    """Return list of Kibitzr CLI extensions"""
    return [
        point.load()
        for point in entrypoints.get_group_all("kibitzr.cli")
    ]


@click.group()
@click.option("-l", "--log-level", default="info",
              type=click.Choice(LOG_LEVEL_CODES.keys()),
              help="Logging level")
@click.pass_context
def cli(ctx, log_level):
    """Run kibitzr COMMAND --help for detailed descriptions"""
    ctx.obj = {'log_level': LOG_LEVEL_CODES[log_level.lower()]}


@cli.command()
def version():
    """Print version"""
    from kibitzr import __version__ as kibitzr_version  # pylint: disable=import-outside-toplevel
    print(kibitzr_version)


@cli.command()
def firefox():
    """Launch Firefox with persistent profile"""
    from kibitzr.app import Application  # pylint: disable=import-outside-toplevel
    Application().run_firefox()


@cli.command()
@click.argument('name', nargs=-1)
@click.pass_context
def once(ctx, name):
    """Run kibitzr checks once and exit"""
    from kibitzr.app import Application  # pylint: disable=import-outside-toplevel
    app = Application()
    sys.exit(app.run(once=True, log_level=ctx.obj['log_level'], names=name))


@cli.command()
@click.argument('name', nargs=-1)
@click.pass_context
def run(ctx, name):
    """Run kibitzr in the foreground mode"""
    from kibitzr.app import Application  # pylint: disable=import-outside-toplevel
    app = Application()
    sys.exit(app.run(once=False, log_level=ctx.obj['log_level'], names=name))


@cli.command()
def init():
    """Create boilerplate configuration files"""
    from kibitzr.app import Application  # pylint: disable=import-outside-toplevel
    Application.bootstrap()


@cli.command()
def telegram_chat():
    """Return chat id for the last message sent to Telegram Bot"""
    # rename import to escape name clashing:
    from kibitzr.app import Application  # pylint: disable=import-outside-toplevel
    app = Application()
    app.telegram_chat()


@cli.command()
def clean():
    """Clean change history"""
    from kibitzr.storage import PageHistory  # pylint: disable=import-outside-toplevel
    PageHistory.clean()


@cli.command()
def stash():
    """Print stash contents"""
    from kibitzr.stash import Stash  # pylint: disable=import-outside-toplevel
    Stash.print_content()


@cli.command()
def reload():
    """Send signal to reload configuration for kibitzr process"""
    from kibitzr.app import Application  # pylint: disable=import-outside-toplevel
    app = Application()
    app.send_reload()


extended_cli = merge_extensions(cli)


if __name__ == "__main__":
    extended_cli()
