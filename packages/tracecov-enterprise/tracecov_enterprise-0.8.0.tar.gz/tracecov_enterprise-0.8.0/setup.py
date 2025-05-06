import sys

from setuptools import setup
from setuptools.command.install import install


class BlockInstall(install):
    def run(self):
        sys.stderr.write(
            "\nERROR: 'tracecov-enterprise' must be installed from a private index.\n"
            "Please configure your installer like this:\n"
            "    uv add tracecov[enterprise] --index tracecov=...\n"
        )
        sys.exit(1)


setup(
    name="tracecov-enterprise",
    version="0.8.0",
    description="Stub package. Install from private index instead.",
    packages=[],
    cmdclass={"install": BlockInstall},
    zip_safe=False,
)
