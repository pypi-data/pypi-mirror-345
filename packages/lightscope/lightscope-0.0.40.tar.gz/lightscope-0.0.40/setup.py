# setup.py
import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.install import install as _install
from distutils.errors import DistutilsError
from distutils.ccompiler import new_compiler
from distutils.sysconfig import customize_compiler

def detect_libpcap():
    """
    Ensure that the pcap.h headers and libpcap.pc (pkg-config) are present.
    """
    # First try pkg-config
    try:
        if subprocess.call(['pkg-config', '--exists', 'libpcap']) == 0:
            return
    except FileNotFoundError:
        # pkg-config itself isn't available; we'll try a compile test
        pass

    # Try a very trivial compile-test for <pcap/pcap.h>
    comp = new_compiler()
    customize_compiler(comp)
    test_code = r'''
    #include <pcap/pcap.h>
    int main(void){ pcap_open_offline(NULL, NULL); return 0; }
    '''
    try:
        # write, compile, and link in a tmp dir
        import tempfile
        tmpdir = tempfile.mkdtemp()
        source = os.path.join(tmpdir, 'test.c')
        with open(source, 'w') as f:
            f.write(test_code)
        obj = comp.compile([source], output_dir=tmpdir)
        comp.link_executable(obj, os.path.join(tmpdir, 'test_exe'))
        return
    except Exception:
        # falls through to error below
        pass

    # Not found  give platformspecific hints
    if sys.platform.startswith('linux'):
        install_cmd = "sudo apt-get install libpcap-dev"
    elif sys.platform == 'darwin':
        install_cmd = "brew install libpcap"
    else:
        install_cmd = "your OS package manager"

    raise DistutilsError(
        "ERROR: Could not find libpcap development headers (pcap.h)!\n\n"
        " On Debian/Ubuntu, run:\n"
        f"    {install_cmd}\n\n"
        " On macOS, make sure you have the Command Line Tools installed\n"
        " (e.g. `xcode-select --install`) and then:\n"
        f"    {install_cmd}\n\n"
        " Afterwards, re-run `pip install .`."
    )


class BuildExt(_build_ext):
    def run(self):
        if sys.platform != 'win32':
            detect_libpcap()
        try:
            super().run()
        except Exception as e:
            raise DistutilsError(
                "Failed to build C extensions.  Make sure you have\n"
                " a working C compiler and libpcap-dev installed."
            ) from e


class Install(_install):
    def run(self):
        if sys.platform != 'win32':
            detect_libpcap()
        super().run()


setup(
    name="lightscope",
    version="0.0.32",
    packages=find_packages(),
    #  your other metadata 
    cmdclass={
        'build_ext': BuildExt,
        'install':   Install,
    },
    # ext_modules=[  ]  # if you actually have a .c extension module
)

