
import click

from . import batch_run_python_script


@click.command()
@click.argument('root')
def main(root):
    """
    process all python file in which folder

    params:

    ROOT: in which folder
    """
    batch_run_python_script(root=root)


if __name__ == '__main__':
    main()