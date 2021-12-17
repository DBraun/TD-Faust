# TD-Faust
[FAUST](https://faust.grame.fr) (Functional Audio Stream) for [TouchDesigner](https://derivative.ca/)

## Overview

TD-Faust is like a very basic version of the online [FAUST IDE](https://faustide.grame.fr/).
* It enables FAUST code to run inside TouchDesigner.
* Tested on Windows and macOS.
* Up to 256 channels of input and 256 channels of output.
* Pick your own block size and sample rate.
* Support for all of the standard [FAUST libraries](https://faustlibraries.grame.fr/) can be used.
* * High-order ambisonics
* * WAV-file playback
* It can automatically generate a UI of native TouchDesigner elements based on the FAUST code. (Help make this better!)
* MIDI data can be passed to FAUST via TouchDesigner CHOPs or hardware.
* It enables [polyphonic MIDI](https://faustdoc.grame.fr/manual/midi/).

Demo:

[![Demo Video Screenshot](https://img.youtube.com/vi/0qi2lp_TgE0/0.jpg)](https://www.youtube.com/watch?v=0qi2lp_TgE0 "FAUST in TouchDesigner (Audio Coding Demo)")

## New to FAUST?

* Browse the suggested [Documentation and Resources](https://github.com/grame-cncm/faust#documentation-and-resources).
* Julius Smith's [Audio Signal Processing in FAUST](https://ccrma.stanford.edu/~jos/aspf/).
* Browse the [Libraries](https://faustlibraries.grame.fr/).
* The [Syntax Manual](https://faustdoc.grame.fr/manual/syntax/).

## Quick Install (Do this even if you compile yourself)

### Windows

Run the latest `win64.exe` installer from FAUST's [releases](https://github.com/grame-cncm/faust/releases). After installing, copy the `.lib` files from `C:/Program Files/Faust/share/faust/` to `C:/Program Files/Derivative/TouchDesigner/share/faust/`.

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download `faust.dll` and `TD-Faust.dll`. Place them in this repository's `Plugins` folder.

### macOS

Run the latest `.dmg` installer from FAUST's [releases](https://github.com/grame-cncm/faust/releases). After installing, copy the `.lib` files from `Faust-2.X/share/faust/` to `/usr/local/share/faust`.

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download `libfaust.2.dylib` and `TD-Faust.plugin`. Place them in this repository's `Plugins` folder.

## Tutorial

You don't need to `import("stdfaust.lib");` in the FAUST dsp code. This line is automatically added for convenience.

## Licenses / Thank You

TD-Faust (MIT-Licensed) relies on these projects/softwares:

* FAUST ([GPL](https://github.com/grame-cncm/faust/blob/master/COPYING.txt)-licensed).
* [pd-faustgen](https://github.com/CICM/pd-faustgen) (MIT-Licensed) provided helpful CMake examples.
* [FaucK](https://github.com/ccrma/chugins/tree/main/Faust) (MIT-Licensed), an integration of FAUST and [ChucK](http://chuck.stanford.edu/).
* [TouchDesigner](https://derivative.ca/)
