# setup.py
import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.install import install as _install
from distutils.errors import DistutilsError

def detect_libpcap():
    """
    Use pkg-config to check for libpcap.  Raises DistutilsError with
    platform‑specific instructions if not found.
    """
    try:
        # this returns 0 if libpcap is available
        rc = subprocess.call(['pkg-config', '--exists', 'libpcap'])
        if rc == 0:
            return
    except FileNotFoundError:
        # pkg-config itself not installed
        pass

    # not found; now build a hint tailored to the platform
    if sys.platform.startswith('linux'):
        install_cmd = "sudo apt-get install libpcap-dev"
    elif sys.platform == 'darwin':
        install_cmd = "brew install libpcap"
    else:
        install_cmd = "consult your OS package manager for libpcap"

    raise DistutilsError(
        " ** Could not find the libpcap development headers **\n"
        " You need to install libpcap so that your system has pcap.h & friends.\n\n"
        f"  On Debian/Ubuntu, run:\n    {install_cmd}\n\n"
        "  Then re-run your pip install."
    )


class BuildExt(_build_ext):
    """Wrap the C‑extension build step so we can catch failures early."""
    def run(self):
        # only check on Unix‑like; on Windows we skip
        if sys.platform != 'win32':
            detect_libpcap()
        try:
            super().run()
        except Exception as e:
            raise DistutilsError(
                "Failed to compile the native extension (after finding libpcap).\n"
                "If the above libpcap hint didn’t help, please check your compiler&build‑tools."
            ) from e


class Install(_install):
    """Wrap install so we still check for libpcap even if there's no extension."""
    def run(self):
        if sys.platform != 'win32':
            detect_libpcap()
        super().run()


setup(
    name="lightscope",
    version="0.0.32",
    packages=find_packages(),
    # … your other metadata here …
    cmdclass={
        'build_ext': BuildExt,
        'install':   Install,
    },
    # ext_modules=[ … ]  # if you have a C extension module
)

