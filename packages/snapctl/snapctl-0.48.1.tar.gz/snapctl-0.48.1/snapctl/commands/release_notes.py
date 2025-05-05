"""
  Release Notes Command
"""
import os
from typing import Union
from snapctl.config.constants import SNAPCTL_INPUT_ERROR
from snapctl.utils.helper import snapctl_error, snapctl_success


class ReleaseNotes:
    """
    Release Notes Command
    """
    SUBCOMMANDS = ["releases", "show"]
    RELEASES_PATH = 'snapctl/data/releases'

    def __init__(self, *, subcommand: str, version: Union[str, None] = None) -> None:
        self.subcommand = subcommand
        self.version = version
        self.validate_input()

    def validate_input(self) -> None:
        """
        Validate input
        """
        if self.subcommand not in self.SUBCOMMANDS:
            snapctl_error(
                message="Invalid command. Valid commands are " +
                f"{', '.join(ReleaseNotes.SUBCOMMANDS)}.",
                code=SNAPCTL_INPUT_ERROR)

    # Upper echelon commands
    def releases(self) -> None:
        """
        List versions
        """
        # List all files and directories in the specified path
        files_and_directories = os.listdir(ReleaseNotes.RELEASES_PATH)

        # Print only files, excluding subdirectories
        print('== Releases ' + '=' * (92))
        for item in files_and_directories:
            if os.path.isfile(os.path.join(ReleaseNotes.RELEASES_PATH, item)):
                print(item.replace('.mdx', '').replace('.md', ''))
        print('=' * (104))
        snapctl_success(message="List versions")

    def show(self) -> None:
        """
        Show version
        """
        # Check if the specified version exists
        version_file = os.path.join(
            ReleaseNotes.RELEASES_PATH, f'{self.version}.mdx')
        if not os.path.isfile(version_file):
            snapctl_error(
                message=f"Version {self.version} does not exist.",
                code=SNAPCTL_INPUT_ERROR)

        # Read the contents of the specified version file
        print('== Releases Notes ' + '=' * (86))
        with open(version_file, 'r') as file:
            print(file.read())
        print('=' * (104))
        snapctl_success(message=f"Show version {self.version}")
