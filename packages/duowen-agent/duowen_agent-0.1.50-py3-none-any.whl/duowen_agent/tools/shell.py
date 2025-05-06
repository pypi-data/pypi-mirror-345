import subprocess
import sys
import warnings

from duowen_agent.tools.base import Tool


class ShellAPIWrapper:
    """Simulates a standalone shell"""

    @staticmethod
    def run(command: str) -> str:
        """
        Runs a command in a subprocess and returns
        the output.

        Args:
            command: The command to run
        """
        try:
            output = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ).stdout.decode()
        except subprocess.CalledProcessError as e:
            output = repr(e)
        return output


def _get_platform() -> str:
    """Get platform."""
    system = sys.platform
    if system == "Darwin":
        return "MacOS"
    return system


class ShellTool(Tool):
    """Tool to run shell commands."""

    name: str = "terminal"
    description: str = f"Run shell commands on this {_get_platform()} machine."

    def _run(self, command: str) -> str:
        warnings.warn(
            "The shell tool has no safeguards by default. Use at your own risk."
        )
        """Run commands and return final output."""
        return ShellAPIWrapper.run(command)
