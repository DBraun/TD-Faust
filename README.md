# TD-Faust

TD-Faust is an integration of [FAUST](https://faust.grame.fr) (**F**unctional **AU**dio **ST**ream) and [TouchDesigner](https://derivative.ca/). The latest builds are for TouchDesigner 2023.11290 and newer. Older TD-Faust builds can be found in the [Releases](https://github.com/DBraun/TD-Faust/releases).

## Overview
 
* FAUST code can be compiled "just-in-time" and run inside TouchDesigner.
* Tested on Windows and macOS.
* Automatically generated user interfaces of TouchDesigner widgets based on the FAUST code.
* Up to 16384 channels of input and 16384 channels of output.
* Pick your own sample rate.
* Support for all of the standard [FAUST libraries](https://faustlibraries.grame.fr/) including
* * High-order ambisonics
* * WAV-file playback
* * Oscillators, noises, filters, and more
* MIDI data can be passed to FAUST via TouchDesigner CHOPs or hardware.
* Support for [polyphonic MIDI](https://faustdoc.grame.fr/manual/midi/).
* * You can address parameters of individual voices (like [MPE](https://en.wikipedia.org/wiki/MIDI#MIDI_Polyphonic_Expression)) or group them together.

Demo / Tutorial:

[![Demo Video Screenshot](https://img.youtube.com/vi/r9oTSwU8ahw/0.jpg)](https://www.youtube.com/watch?v=r9oTSwU8ahw "FAUST in TouchDesigner (Audio Coding Demo)")

Examples of projects made with TD-Faust can be found [here](https://github.com/DBraun/TD-Faust/wiki/Made-With-TD-Faust). Contributions are welcome!

## New to FAUST?

* Browse the suggested [Documentation and Resources](https://github.com/grame-cncm/faust#documentation-and-resources).
* Develop code in the [FAUST IDE](https://faustide.grame.fr/).
* Read [Faust-Tutorial](https://github.com/DBraun/Faust-Tutorial) by [@DBraun](https://github.com/DBraun/).
* Read Julius Smith's [Audio Signal Processing in FAUST](https://ccrma.stanford.edu/~jos/aspf/).
* Browse the [Libraries](https://faustlibraries.grame.fr/) and their [source code](https://github.com/grame-cncm/faustlibraries).
* Read the [Syntax Manual](https://faustdoc.grame.fr/manual/syntax/).

## Quick Install

### Windows

#### Pre-compiled

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download and unzip the latest Windows version. Copy `TD-Faust.dll` and the `faustlibraries` folder to this repository's `Plugins` folder. Open `TD-Faust.toe` and compile a few examples.

#### Compiling locally

If you need to compile `TD-Faust.dll` yourself, you should first install [Python 3.11](https://www.python.org/downloads/release/python-3117/) to `C:/Python311/` and confirm it's in your system PATH. You'll also need Visual Studio 2022 and CMake. Then open a "x64 Native Tools for Visual Studio" command prompt with Administrator privileges to this repo's root directory and run `python build_tdfaust.py`.

### macOS

#### Pre-compiled

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download and unzip the latest macOS version. Users with "Apple Silicon" computers should download "arm64". Copy `TD-Faust.plugin` and `Reverb.plugin` to this repository's `Plugins` folder.

Open `TD-Faust.toe` and compile a few examples.

#### Compiling locally

1. Clone this repository with git. Then update all submodules in the root of the repository with `git submodule update --init --recursive`
2. Install Xcode.
3. [Install CMake](https://cmake.org/download/) and confirm that it's installed by running `cmake --version` in Terminal. You may need to run `export PATH="/Applications/CMake.app/Contents/bin":"$PATH"`
4. Install requirements with [brew](http://brew.sh/): `brew install autoconf autogen automake flac libogg libtool libvorbis opus mpg123 pkg-config`
5. In the same Terminal window, navigate to the root of this repository and run `python3 build_tdfaust.py --pythonver=3.11`
6. Open `TD-Faust.toe`

## Building a Custom Operator

We have previously described a multi-purpose CHOP that dynamically compiles Faust code inside TouchDesigner. Although it's powerful, you have to specify the DSP code, press the `compile` parameter, and only then do the CHOP's parameters appear. In contrast, ordinary [CHOPs](https://docs.derivative.ca/CHOP) can be created from the [OP Create Dialog](https://docs.derivative.ca/OP_Create_Dialog) and already have parameters, but they are narrower in purpose. What if you want to use Faust to create a more single-purpose Reverb CHOP with these advantages? In this case, you should use the `faust2touchdesigner.py` script.

These are the requirements:
* Pick a Faust DSP file such as `reverb.dsp` that defines a `process = ...;`.
* Python should be installed.
* CMake should be installed.

If on Windows, you should open an "x64 Native Tools for Visual Studio" command prompt. On macOS, you can use Terminal. Then run a variation of the following script:

```bash
python faust2td.py --dsp reverb.dsp --type "Reverb" --label "Reverb" --icon "Rev" --author "David Braun" --email "github.com/DBraun" --drop-prefix
```

Limitations and Gotchas:
* Use `python3` on macOS.
* The example script above overwrites `Faust_Reverb_CHOP.h`, `Faust_Reverb_CHOP.cpp`, and `Reverb.h`, so avoid changing those files later.
* [Polyphonic](https://faustdoc.grame.fr/manual/midi/#standard-polyphony-parameters) instruments have not been implemented.
* MIDI has not been implemented.
* The [`soundfile`](https://faustdoc.grame.fr/manual/syntax/#soundfile-primitive) primitive has not been implemented ([`waveform`](https://faustdoc.grame.fr/manual/syntax/#waveform-primitive) is ok!)
* CHOP Parameters are not "smoothed" automatically, so you may want to put `si.smoo` after each [`hslider`](https://faustdoc.grame.fr/manual/syntax/#hslider-primitive)/[`vslider`](https://faustdoc.grame.fr/manual/syntax/#vslider-primitive).
* File a GitHub issue with any other problems or requests. Pull requests are welcome too!

## Tutorial

### Writing Code

You don't need to `import("stdfaust.lib");` in the FAUST dsp code. This line is automatically added for convenience.

### Custom Parameters in TouchDesigner

* Sample Rate: Audio sample rate (such as 44100 or 48000).
* Polyphony: Toggle whether polyphony is enabled. Refer to the [Faust guide to polyphony](https://faustdoc.grame.fr/manual/midi/) and use the keywords such as `gate`, `gain`, and `freq` when writing the DSP code.
* N Voices: The number of polyphony voices.
* Group Voices: Toggle group voices (see below).
* Dynamic Voices: Toggle dynamic voices (see below).
* MIDI: Toggle whether **hardware** MIDI input is enabled. 
* MIDI In Virtual: Toggle whether **virtual** MIDI input is enabled (**macOS support only**)
* MIDI In Virtual Name: The name of the virtual MIDI input device (**macOS support only**)
* Code: The DAT containing the Faust code to use.
* Faust Libraries Path: The directory containing your custom faust libraries (`.lib` files)
* Assets Path: The directory containing your assets such as `.wav` files.
* Compile: Compile the Faust code.
* Reset: Clear the compiled code, if there is any.
* Clear MIDI: Clear the MIDI notes (in case notes are stuck on).
* Viewer COMP: The [Container COMP](https://docs.derivative.ca/Container_COMP) which will be used when `Compile` is pulsed.

### Python API

The Faust CHOP's Python interface is similar to the [Audio VST CHOP](https://docs.derivative.ca/AudiovstCHOP_Class).

* `sendNoteOn(channel: int, note: int, velocity: int, noteOffDelay: float=None, noteOffVelocity: int=None) -> None` (**`noteOffDelay` and `noteOffVelocity` aren't used yet**)
* `sendNoteOff(channel: int, note: int, velocity: int) -> None`
* `panic() -> None`
* `sendAllNotesOff(channel: int) -> None`
* `sendControl(channel: int, ctrl: int, value: int) -> None`
* `sendPitchBend(channel: int, wheel: int) -> None`
* `sendProgram(channel: int, pgm: int) -> None`

### Automatic Custom Parameters and UI

One great feature of TD-Faust is that user interfaces that appear in the Faust code become [Custom Parameters](https://docs.derivative.ca/Custom_Parameters) on the Faust Base. If a Viewer COMP is set, then it can be automatically filled in with widgets with [binding](https://docs.derivative.ca/Binding). Look at the simple Faust code below:

```faust
import("stdfaust.lib");
freq = hslider("Freq", 440, 0, 20000, 0) : si.smoo;
gain = hslider("Volume[unit:dB]", -12, -80, 20, 0) : si.smoo : ba.db2linear;
process = freq : os.osc : _*gain <: si.bus(2);
```

If you compile this with a Faust Base, the Base will create a "Control" page of custom parameters. Because of the code we've written, there will be two Float parameters named "Freq" and "Volume". In order to automatically create a UI, pressing compile will save a JSON file inside a directory called `dsp_output`. These files are meant to be temporary and are deleted each time `TD-Faust.toe` opens.

### Group Voices and Dynamic Voices

The `Group Voices` and `Dynamic Voices` toggles matter when using [polyphony](https://faustdoc.grame.fr/manual/midi/).

If you enable `Group Voices`, one set of parameters will control all voices at once. Otherwise, you will need to address a set of parameters for each voice.

If you enable `Dynamic Voices`, then voices whose notes have been released will be dynamically turned off in order to save computation. Dynamic Voices should be on in most cases such as when you're wiring a MIDI buffer as the third input to the Faust CHOP. There is a special case in which you might want `Dynamic Voices` off:
* You are not wiring a MIDI buffer as the third input.
* `Group Voices` is off.
* You are individually addressing the frequencies, gates and/or gains of the polyphonic voices. This step works as a replacement for the lack of the wired MIDI buffer.

### Control Rate and Sample Rate

The sample rate is typically a high number such as 44100 Hz, and the control rate of UI parameters might be only 60 Hz. This can lead to artifacts. Suppose we are listening to a 44.1 kHz signal, but we are multiplying it by a 60 Hz "control" signal such as a TouchDesigner parameter meant to control the volume.

```faust
import("stdfaust.lib");
volume = hslider("Volume", 1., 0., 1., 0);
process = os.osc(440.)*volume <: si.bus(2);
```

In TouchDesigner, we can press "Compile" to get a "Volume" custom parameter on the "Control" page of the Faust base. You can look inside the base to see how the custom parameter is wired into the Faust CHOP. By default, this "Volume" signal will only be the project cook rate (60 Hz). Therefore, as you change the volume, you will hear artifacts in the output. To reduce artifacts, there are three solutions:

1. Use [si.smoo](https://faustlibraries.grame.fr/libs/signals/#sismoo) or [si.smooth](https://faustlibraries.grame.fr/libs/signals/#sismooth) to smooth the control signal: `volume = hslider("Volume", 1., 0., 1., 0) : si.smoo;`

2. Create a higher sample-rate control signal, possibly as high as the Faust CHOP, and connect it as the second input to the Faust base.

3. Re-design your code so that high-rate custom parameters are actually input signals.
```faust
import("stdfaust.lib");
// "volume" is now an input signal
process = _ * os.osc(440.) <: si.bus(2);
```
You could then connect a high-rate single-channel "volume" CHOP to the first input of the Faust Base.

### Using TD-Faust in New Projects

From this repository, copy the `toxes/FAUST` structure into your new project. You should have:

* `MyProject/MyProject.toe`
* `MyProject/toxes/FAUST/FAUST.tox`

and any other files which are sibling to FAUST.tox

Now drag `FAUST.tox` into your new TouchDesigner project, probably near the root. `FAUST.tox` acts as a [Global OP Shortcut](https://docs.derivative.ca/Global_OP_Shortcut). Next, copy `toxes/FAUST/main_faust_base.tox` into the project and use it in a way similar to how it's used in `TD-Faust.toe`.

## Licenses / Thank You

TD-Faust (GPL-Licensed) relies on these projects/softwares:

* FAUST ([GPL](https://github.com/grame-cncm/faust/blob/master/COPYING.txt)-licensed).
* [FaucK](https://github.com/ccrma/chugins/tree/main/Faust) (MIT-Licensed), an integration of FAUST and [ChucK](http://chuck.stanford.edu/).
* [TouchDesigner](https://derivative.ca/) [License](https://derivative.ca/end-user-license-agreement-eula)
