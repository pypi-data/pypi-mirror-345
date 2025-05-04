import click
from fixify.core import fixify

 # assuming your class is in fixify.py

@click.command()
@click.option('--heyai', help='Ask something to your AI buddy')
@click.option('--explain', nargs=3, type=str, help='Explain code from a file: filepath start_line end_line')
def cli(heyai, explain):
    fix = fixify()

    if heyai:
        fix.heyAI(heyai)
    elif explain:
        filepath, start_line, end_line = explain
        fix.explainFromFile(filepath, int(start_line), int(end_line))

if __name__ == '__main__':
    cli()
