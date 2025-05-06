# setup.py
import sys
from distutils.errors import DistutilsError

def detect_libpcap():
    try:
        import subprocess
        if subprocess.call(['pkg-config','--exists','libpcap']) == 0:
            return
    except Exception:
        pass

    # quick compile test
    try:
        from distutils.ccompiler import new_compiler
        from distutils.sysconfig  import customize_compiler
        comp = new_compiler()
        customize_compiler(comp)
        import tempfile, os
        td = tempfile.mkdtemp()
        src = os.path.join(td,'t.c')
        open(src,'w').write('#include <pcap/pcap.h>\nint main(){}')
        obj = comp.compile([src], output_dir=td)
        comp.link_executable(obj, os.path.join(td,'a.out'))
        return
    except Exception:
        pass

    if sys.platform.startswith('linux'):
        hint = 'sudo apt-get install libpcap-dev'
    elif sys.platform == 'darwin':
        hint = 'brew install libpcap'
    else:
        hint = '<your OS package manager> install libpcap-dev'

    raise DistutilsError(
        "ERROR: libpcap headers not found.\n"
        f"Please run:\n    {hint}\n"
        "and then rerun `pip install .`"
    )

# fail as early as possible:
if sys.platform != 'win32':
    detect_libpcap()


# now the normal setuptools boilerplate:
from setuptools import setup, find_packages

setup(
    name="lightscope",
    version="0.0.32",
    packages=find_packages(),
    # 
)

