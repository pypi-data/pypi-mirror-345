# setup.py
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.install import install as _install
from distutils.errors import DistutilsError

class BuildExt(_build_ext):
    """Wrap the C‑extension build step so we can catch failures and
    print a friendlier hint (e.g. “you need libpcap-dev”)."""
    def run(self):
        try:
            super().run()
        except Exception as e:
            raise DistutilsError(
                "Failed to compile the native extension.\n"
                "It looks like you are missing the libpcap headers.\n"
                "On Debian/Ubuntu run:\n"
                "  sudo apt-get install libpcap-dev\n"
                "On Red Hat/CentOS run:\n"
                "  sudo yum install libpcap-devel\n"
            ) from e

class Install(_install):
    """Wrap the install step to detect non‑root or missing perms."""
    def run(self):
        # example: require you to be root
        if os.name == "posix" and os.geteuid() != 0:
            sys.exit(
                "\nERROR: lightscope must be installed as root (needs raw‐socket permissions).\n"
                "Please run:\n"
                "  sudo pip install lightscope\n"
            )
        super().run()

setup(
    name="lightscope",
    version="0.0.21",
    packages=find_packages(),
    # ... your other metadata ...
    cmdclass={
        'build_ext': BuildExt,
        'install':   Install,
    },
    # if you have a C extension:
    # ext_modules=[ ... ],
)

