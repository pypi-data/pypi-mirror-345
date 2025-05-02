# main.py
import click

@click.group()
def cli():
    """Mon super CLI."""
    pass

@cli.command()
@click.argument("name")
def hello(name):
    """Greets the user with a hello message."""
    click.echo(f"Hello, {name}!")

@cli.command()
@click.argument('a', type=int)
@click.argument('b', type=int)
def add(a, b):
    """Additionne deux nombres."""
    result = a + b
    click.echo(f"Le résultat de {a} + {b} est {result}")

@cli.command()
@click.argument('a', type=int)
@click.argument('b', type=int)
def sub(a, b):
    """Additionne deux nombres."""
    result = a - b
    click.echo(f"Le résultat de {a} - {b} est {result}")
               
@cli.command()
@click.argument('a', type=int)
@click.argument('b', type=int)
def multi(a, b):
    """Additionne deux nombres."""
    result = a * b
    click.echo(f"Le résultat de {a} * {b} est {result}")
	
if __name__ == '__main__':
    cli()

