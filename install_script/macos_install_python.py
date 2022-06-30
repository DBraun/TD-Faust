# This project is licensed under the 'BSD 2-clause license'.

# Copyright (c) 2017-2019, Joe Rickerby and contributors. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from pathlib import Path
import os
import ssl
import urllib.request
import subprocess
import certifi
import shlex
import shutil

from typing import Union, Optional


install_certifi_script = Path(__file__).parent / "install_certifi.py"

def download(url: str, dest: Path) -> None:
    print(f"+ Download {url} to {dest}")
    dest_dir = dest.parent
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True)

    # we've had issues when relying on the host OS' CA certificates on Windows,
    # so we use certifi (this sounds odd but requests also does this by default)
    cafile = os.environ.get("SSL_CERT_FILE", certifi.where())
    context = ssl.create_default_context(cafile=cafile)
    repeat_num = 3
    for i in range(repeat_num):
        try:
            response = urllib.request.urlopen(url, context=context)
        except Exception:
            if i == repeat_num - 1:
                raise
            sleep(3)
            continue
        break

    try:
        dest.write_bytes(response.read())
    finally:
        response.close()


PathOrStr = Union[str, "os.PathLike[str]"]


def call(
    *args: PathOrStr,
) -> Optional[str]:
    """
    Run subprocess.run, but print the commands first. Takes the commands as
    *args. Uses shell=True on Windows due to a bug. Also converts to
    Paths to strings, due to Windows behavior at least on older Pythons.
    https://bugs.python.org/issue8557
    """
    args_ = [str(arg) for arg in args]
    # print the command executing for the logs
    print("+ " + " ".join(shlex.quote(a) for a in args_))
    result = subprocess.run(args_, check=True, shell=False, env=None, cwd=None)
    return None


SYMLINKS_DIR = Path("/tmp/cibw_bin")


def make_symlinks(installation_bin_path: Path, python_executable: str, pip_executable: str) -> None:
    assert (installation_bin_path / python_executable).exists()

    # Python bin folders on Mac don't symlink `python3` to `python`, and neither
    # does PyPy for `pypy` or `pypy3`, so we do that so `python` and `pip` always
    # point to the active configuration.
    if SYMLINKS_DIR.exists():
        shutil.rmtree(SYMLINKS_DIR)
    SYMLINKS_DIR.mkdir(parents=True)

    (SYMLINKS_DIR / "python").symlink_to(installation_bin_path / python_executable)
    (SYMLINKS_DIR / "python-config").symlink_to(
        installation_bin_path / (python_executable + "-config")
    )
    (SYMLINKS_DIR / "pip").symlink_to(installation_bin_path / pip_executable)


def install_cpython(tmp: Path, version: str, url: str) -> Path:
    installation_path = Path(f"/Library/Frameworks/Python.framework/Versions/{version}")
    pkg_path = tmp / "Python.pkg"
    # download the pkg
    download(url, pkg_path)
    # install
    call("sudo", "installer", "-pkg", pkg_path, "-target", "/")
    pkg_path.unlink()
    call(installation_path / "bin" / "python3", install_certifi_script)

    return installation_path / "bin" / "python3"


def main():

    tmp = Path("/tmp/cibw_tmp")
    version = "3.9"
    url = "https://www.python.org/ftp/python/3.9.9/python-3.9.9-macos11.pkg"

    base_python = install_cpython(tmp, version, url)
    assert base_python.exists()

if __name__ == '__main__':
    main()
