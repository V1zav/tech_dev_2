import os
from daphne.cli import CommandLineInterface

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    CommandLineInterface.entrypoint()
