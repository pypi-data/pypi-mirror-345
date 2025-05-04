from dektools.typer import command_version
from . import app
from .image import app as image_app

command_version(app, __name__)
app.add_typer(image_app, name='image')


def main():
    app()
