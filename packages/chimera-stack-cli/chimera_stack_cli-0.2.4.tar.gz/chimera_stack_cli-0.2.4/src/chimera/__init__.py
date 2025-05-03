"""
ChimeraStack CLI - A template-based development environment manager.

A powerful tool for creating preconfigured development environments with Docker.
"""

from importlib.metadata import version as _pkg_version, PackageNotFoundError

try:  # runtime wheel / sdist
    __version__ = _pkg_version("chimera-stack-cli")
except PackageNotFoundError:  # editable install
    from setuptools_scm import get_version
    __version__ = get_version(root='../..', relative_to=__file__)

__author__ = "Amirofcodes"
__email__ = "amirofcodes20@gmail.com"
__license__ = "MIT"
__repository__ = "https://github.com/Amirofcodes/ChimeraStack_CLI"
__description__ = "A powerful development environment manager that helps you quickly set up and manage local development environments using pre-configured templates."
