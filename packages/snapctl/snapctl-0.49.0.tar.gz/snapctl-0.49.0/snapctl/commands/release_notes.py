"""
  Release Notes
"""
from typing import Union
import importlib.resources as pkg_resources
import snapctl.data.releases  # must have __init__.py under releases
from snapctl.config.constants import SNAPCTL_INPUT_ERROR
from snapctl.utils.helper import snapctl_error, snapctl_success


class ReleaseNotes:
    """
    Release Notes Command
    """
    SUBCOMMANDS = ["releases", "show"]

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

    def releases(self) -> None:
        """
        List versions
        """
        print('== Releases ' + '=' * (92))
        # List all resource files in snapctl.data.releases
        for resource in pkg_resources.contents(snapctl.data.releases):
            if resource.endswith('.mdx'):
                print(resource.replace('.mdx', '').replace('.md', ''))
        print('=' * (104))
        snapctl_success(message="List versions")

    def show(self) -> None:
        """
        Show version
        """
        version_filename = f"{self.version}.mdx"

        if version_filename not in pkg_resources.contents(snapctl.data.releases):
            snapctl_error(
                message=f"Version {self.version} does not exist.",
                code=SNAPCTL_INPUT_ERROR)

        print('== Release Notes ' + '=' * (86))
        with pkg_resources.open_text(snapctl.data.releases, version_filename) as file:
            print(file.read())
        print('=' * (104))
        snapctl_success(message=f"Show version {self.version}")
