#!/usr/bin/env python3
"""
lightscope_updater.py

Autoupdate wrapper for lightscope_core.py that:
 1. Ensures lightscope is installed
 2. Launches lightscope_core.py as a subprocess
 3. Every hour, polls PyPI for a newer lightscope version
 4. If found, gracefully restarts the core app under the new version
"""

import sys
import time
import signal
import subprocess
import urllib.request, json
from importlib import metadata
from packaging.version import parse as parse_version

# how often to check for new releases (seconds)
CHECK_INTERVAL = 60 * 60  # 1h

PYPI_JSON_URL = "https://pypi.org/pypi/lightscope/json"
SCRIPT = "lightscope_core.py"  # your main entrypoint


def get_installed_version():
    try:
        return metadata.version("lightscope")
    except metadata.PackageNotFoundError:
        return None


def get_latest_version():
    try:
        with urllib.request.urlopen(PYPI_JSON_URL) as resp:
            data = json.load(resp)
        return data["info"]["version"]
    except Exception as e:
        print(f"[Updater]  failed to fetch PyPI data: {e}", file=sys.stderr)
        return None


def install_or_upgrade():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "lightscope"])


def spawn_app():
    return subprocess.Popen([sys.executable, SCRIPT])


def graceful_shutdown(proc, timeout=30):
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("[Updater] process didnt exit in time, killing", file=sys.stderr)
        proc.kill()
        proc.wait()


def main():
    # 1) ensure we have it installed
    v0 = get_installed_version()
    if not v0:
        print("[Updater] lightscope not installed; installing")
        install_or_upgrade()
        v0 = get_installed_version()
        if not v0:
            print("[Updater] install failed; exiting", file=sys.stderr)
            sys.exit(1)
    print(f"[Updater] running lightscope {v0}")

    # 2) launch core
    proc = spawn_app()

    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            latest = get_latest_version()
            if not latest:
                continue

            if parse_version(latest) > parse_version(v0):
                print(f"[Updater] new version available: {latest} (installed {v0}), upgrading")
                graceful_shutdown(proc)

                try:
                    install_or_upgrade()
                except subprocess.CalledProcessError as e:
                    print(f"[Updater] pip upgrade failed: {e}", file=sys.stderr)
                    proc = spawn_app()
                    continue

                v0 = get_installed_version()
                print(f"[Updater] restarted lightscope {v0}")
                proc = spawn_app()

    except KeyboardInterrupt:
        print("[Updater] caught SIGINT, shutting down")
        graceful_shutdown(proc)
        sys.exit(0)


if __name__ == "__main__":
    main()

