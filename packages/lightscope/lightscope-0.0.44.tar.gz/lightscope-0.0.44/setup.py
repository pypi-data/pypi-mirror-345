# setup.py
import sys
from distutils.errors import DistutilsError

def detect_libpcap():
    import subprocess, tempfile, os
    from distutils.ccompiler import new_compiler
    from distutils.sysconfig  import customize_compiler

    # 1) pkg‑config check
    try:
        if subprocess.call(["pkg-config","--exists","libpcap"]) == 0:
            return
    except Exception:
        pass

    # 2) compile‐and‐link‐tiny‐C test
    try:
        comp = new_compiler()
        customize_compiler(comp)
        td = tempfile.mkdtemp()
        src = os.path.join(td, "t.c")
        open(src,"w").write('#include <pcap/pcap.h>\nint main(){}')
        obj = comp.compile([src], output_dir=td)
        comp.link_executable(obj, os.path.join(td, "a.out"))
        return
    except Exception:
        pass

    # 3) if we get here, no pcap headers
    if sys.platform.startswith("linux"):
        hint = "sudo apt-get install libpcap-dev"
    elif sys.platform == "darwin":
        hint = "brew install libpcap"
    else:
        hint = "<your OS package manager> install libpcap-dev"

    raise DistutilsError(
        "ERROR: libpcap headers not found.\n"
        f"Please run:\n    {hint}\n"
        "and then rerun `pip install .`"
    )


# fail as early as possible on Unix‑like
if sys.platform != "win32":
    detect_libpcap()


from setuptools import setup, find_packages

setup(
    name="lightscope",
    version="0.0.44",
    packages=find_packages(),
    # you can leave out entry_points here if you already declared them in pyproject.toml
    # if you did want to duplicate them:
    # entry_points={
    #   "console_scripts": {
    #     "lightscope = lightscope.lightscope:main",
    #     "lightscope_no_auto_update = lightscope.lightscope_core:lightscope_run",
    #   }
    # },
    # cmdclass=… only needed if you want to hook build_ext/install rather than top‑level import
)

