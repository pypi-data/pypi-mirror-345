"""Custom build script for the 1Shot API Python client."""

import os
import shutil
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Custom build hook for the 1Shot API Python client."""

    def initialize(self, version, build_data):
        """Initialize the build hook.

        Args:
            version: The version being built
            build_data: The build data
        """
        # Get the source and build directories
        src_dir = Path("src")
        build_dir = Path("dist")

        # Create the build directory if it doesn't exist
        build_dir.mkdir(exist_ok=True)

        # Copy the README to the build directory
        shutil.copy("README.md", build_dir / "README.md")

        # Copy the license to the build directory
        if os.path.exists("LICENSE"):
            shutil.copy("LICENSE", build_dir / "LICENSE") 