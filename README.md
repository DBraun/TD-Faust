# TD-Faust
[FAUST](https://faust.grame.fr) (Functional Audio Stream) for [TouchDesigner](https://derivative.ca/)

## Overview

TD-Faust is like a very basic version of the online [FAUST IDE](https://faustide.grame.fr/).
* Only tested on Windows (If you try OSX, tell us!).
* It enables FAUST code to run inside TouchDesigner.
* Up to 256 channels of input and 256 channels of output.
* Pick your own block size and sample rate.
* Any of the standard [FAUST libraries](https://faustlibraries.grame.fr/) can be used.
* It can automatically generate a UI of native TouchDesigner elements based on the FAUST code. (Help make this better!)
* It enables [polyphonic MIDI](https://faustdoc.grame.fr/manual/midi/) control with MIDI hardware.

## New to FAUST?

* Browse the suggested [Documentation and Resources](https://github.com/grame-cncm/faust#documentation-and-resources).
* Julius Smith's [Audio Signal Processing in FAUST](https://ccrma.stanford.edu/~jos/aspf/).
* Browse the [Libraries](https://faustlibraries.grame.fr/).
* The [Syntax Manual](https://faustdoc.grame.fr/manual/syntax/).

## Quick Install (Do this even if you compile yourself)

Run the latest `win64.exe` installer from FAUST's [releases](https://github.com/grame-cncm/faust/releases). After installing, copy the `.lib` files from `C:/Program Files/Faust/share/faust/` to `C:/Program Files/Derivative/TouchDesigner/share/faust/`. On OSX, copy them to either `/usr/local/share/faust` or `/usr/share/faust`.

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download `faust.dll` and `TD-Faust.dll`. Place them in this repository's `Plugins` folder. That's all. The remaining instructions are for compiling.

## Full Compilation

### Git Submodules

git submodule update in this repo: `git submodule update --init --recursive`. This should clone `llvm-project` and `FAUST` to the `thirdparty` folder.

### Building LLVM
```bash
cd thirdparty/llvm-project/llvm
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019" -DLLVM_USE_CRT_DEBUG=MDd -DLLVM_USE_CRT_RELEASE=MD -DLLVM_BUILD_TESTS=Off -DCMAKE_INSTALL_PREFIX="./llvm" -Thost=x64`
```

(Note that the MD flags build a dynamic library, whereas MT would have built a static library.)

Then open `thirdparty/llvm-project/llvm/build/LLVM.sln` and build in Release/64. This will take at least 20 minutes.

### Building TD-Faust
Then in root of TD-Faust repo, set an absolute path to this subfolder in your llvm-project installation. Then run CMake.
```bash
set LLVM_DIR=C:/tools/TD-Faust/thirdparty/llvm-project/llvm/build/lib/cmake/llvm
mkdir build
cd build
cmake .. -DUSE_LLVM_CONFIG=off
```

Then open `TD-Faust.sln` and build in Release mode. (Debug is inconvenient because you'd have to build LLVM in Debug.) `TD-Faust.dll` and `faust.dll` should appear in the Plugins folder.

Run the TouchDesigner project by pressing `F5`.

## Licenses / Thank You

TD-Faust (MIT-Licensed) relies on these projects/softwares:

* FAUST ([GPL](https://github.com/grame-cncm/faust/blob/master/COPYING.txt)-licensed).
* [pd-faustgen](https://github.com/CICM/pd-faustgen) (MIT-Licensed) provided helpful CMake examples.
* [FaucK](https://github.com/ccrma/chugins/tree/main/Faust) (MIT-Licensed), an integration of FAUST and [ChucK](http://chuck.stanford.edu/).
* [TouchDesigner](https://derivative.ca/)
