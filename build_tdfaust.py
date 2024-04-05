import argparse
import os
import platform
import subprocess
import shlex


def run_command(command, shell=False):
    subprocess.run(command, shell=shell, check=True)

def build_windows(pythonver: str):
    os.system('rm build/CMakeCache.txt')

    # Download libsndfile
    libsndfile_dir = "thirdparty/libsndfile-1.2.0-win64/"
    if not os.path.exists(libsndfile_dir):
        print("Downloading libsndfile...")
        os.chdir('thirdparty')
        run_command(["curl", "-OL", "https://github.com/libsndfile/libsndfile/releases/download/1.2.0/libsndfile-1.2.0-win64.zip"])
        run_command(["7z", "x", "libsndfile-1.2.0-win64.zip", "-y"])
        os.remove("libsndfile-1.2.0-win64.zip")
        print("Downloaded libsndfile.")
        os.chdir("..")

    # Build with CMake
    cmake_command = [
        "cmake", "-Bbuild", "-DCMAKE_BUILD_TYPE=Release",
        "-DLIBFAUST_DIR=thirdparty/libfaust/win64/Release",
        "-DSndFile_DIR=thirdparty/libsndfile/build",
        f"-DPYTHONVER={pythonver}"
    ]
    run_command(cmake_command)
    run_command(["cmake", "--build", "build", "--config", "Release"])
    os.system(f'cp "thirdparty/libsndfile-1.2.0-win64/bin/sndfile.dll" "Plugins/sndfile.dll"')

def build_macos(pythonver: str, touchdesigner_app: str, arch: str=None):
    os.system('rm -r Plugins/TD-Faust.plugin')

    cmake_osx_deployment_target = f"-DCMAKE_OSX_DEPLOYMENT_TARGET=12.0"
    if arch == 'arm64':
        libfaust_dir = f"{os.getcwd()}/thirdparty/libfaust/darwin-arm64/Release"
        cmake_build_arch = f"-DCMAKE_OSX_ARCHITECTURES=arm64"
    elif arch == 'x86_64':
        libfaust_dir = f"{os.getcwd()}/thirdparty/libfaust/darwin-x64/Release"
        cmake_build_arch = f"-DCMAKE_OSX_ARCHITECTURES=x86_64"
    else:
        raise RuntimeError(f"Unknown CPU architecture: {arch}.")

    # Build libsndfile
    print("Building libsndfile.")
    os.chdir("thirdparty/libsndfile")
    run_command(["cmake", "-Bbuild", "-DCMAKE_VERBOSE_MAKEFILE=ON", "-DCMAKE_INSTALL_PREFIX=./install", cmake_osx_deployment_target, cmake_build_arch])
    run_command(["cmake", "--build", "build", "--config", "Release"])
    run_command(["cmake", "--build", "build", "--target", "install"])
    os.chdir("../..")

    # Build with CMake
    cmake_command = [
        "cmake", "-Bbuild", "-G", "Xcode",
        f"-DLIBFAUST_DIR={libfaust_dir}",
        f"-DPYTHONVER={pythonver}",
        f"-DPython_ROOT_DIR={touchdesigner_app}/Contents/Frameworks/Python.framework/Versions/{pythonver}",
        cmake_osx_deployment_target,
        cmake_build_arch
    ]
    run_command(cmake_command)
    run_command(["cmake", "--build", "build", "--config", "Release"])
    os.system('mv build/Release/TD-Faust.plugin Plugins')
    if 'CMAKE_XCODE_ATTRIBUTE_DEVELOPMENT_TEAM' in os.environ:
        CMAKE_XCODE_ATTRIBUTE_DEVELOPMENT_TEAM = os.environ['CMAKE_XCODE_ATTRIBUTE_DEVELOPMENT_TEAM']
        subprocess.call(shlex.split(f'codesign --force --verify --verbose=2 --timestamp --options=runtime --deep --sign "Developer ID Application: David Braun ({CMAKE_XCODE_ATTRIBUTE_DEVELOPMENT_TEAM})" build/Release/TD-Faust.plugin'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build TD-Faust plugin for Windows or macOS.")
    parser.add_argument("--pythonver", default="3.11", help="Specify the Python version.")
    parser.add_argument("--touchdesigner_app", default="/Applications/TouchDesigner.app", help="Path to TouchDesigner app (macOS only).")
    parser.add_argument("--arch", default=platform.machine(), help="CPU Architecture for which to build.")
    args = parser.parse_args()

    if platform.system() == "Windows":
        build_windows(args.pythonver)
    elif platform.system() == "Darwin":
        build_macos(args.pythonver, args.touchdesigner_app, args.arch)
    else:
        raise RuntimeError(f"Unsupported operating system: {platform.system()}.")
