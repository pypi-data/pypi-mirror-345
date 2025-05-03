"""Script entry points for Poetry."""

import subprocess
import sys


def test():
    """Run pytest with coverage."""
    sys.exit(
        subprocess.run(
            ["pytest", "-v", "--cov=zmp_md_translator", "--cov-report=term-missing"]
        ).returncode
    )


def watch():
    """Run pytest-watch with coverage."""
    sys.exit(
        subprocess.run(
            [
                "ptw",
                "--runner",
                "pytest -v --cov=zmp_md_translator --cov-report=term-missing",
            ]
        ).returncode
    )
