import os

import click


def detect_output_file_exist(basedir, imgname, outputformat, overwrite):
    filename = '{}.{}'.format(imgname, outputformat)
    filename = os.path.join(basedir, filename)

    if os.path.exists(filename) and not overwrite:
        click.echo('output image file exists. i will give it up.')
        return None
    return filename