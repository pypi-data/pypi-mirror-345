from .comment import comment
from .create import create
from .dump import dump
from .edit import edit
from .list import list
from .login import login, setpassword
from .show import show
from .cli import main


def main():
    cli.main()
