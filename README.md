# TD-Faust
TD-Faust is an integration of [FAUST](https://faust.grame.fr) (Functional Audio Stream) and [TouchDesigner](https://derivative.ca/).

## Overview
 
* FAUST code can be compiled "just-in-time" and run inside TouchDesigner.
* Tested on Windows and macOS.
* Automatically generated user interfaces of native TouchDesigner elements based on the FAUST code.
* Up to 256 channels of input and 256 channels of output.
* Pick your own sample rate.
* Support for all of the standard [FAUST libraries](https://faustlibraries.grame.fr/) including
* * High-order ambisonics
* * WAV-file playback
* * Oscillators, noises, filters, and more
* MIDI data can be passed to FAUST via TouchDesigner CHOPs or hardware.
* Support for [polyphonic MIDI](https://faustdoc.grame.fr/manual/midi/).
* * You can address parameters of individual voices (like [MPE](https://en.wikipedia.org/wiki/MIDI#MIDI_Polyphonic_Expression)) or group them together.

Demo:

[![Demo Video Screenshot](https://img.youtube.com/vi/0qi2lp_TgE0/0.jpg)](https://www.youtube.com/watch?v=0qi2lp_TgE0 "FAUST in TouchDesigner (Audio Coding Demo)")

## New to FAUST?

* Browse the suggested [Documentation and Resources](https://github.com/grame-cncm/faust#documentation-and-resources).
* Develop code in the [FAUST IDE](https://faustide.grame.fr/).
* Read Julius Smith's [Audio Signal Processing in FAUST](https://ccrma.stanford.edu/~jos/aspf/).
* Browse the [Libraries](https://faustlibraries.grame.fr/) and their [source code](https://github.com/grame-cncm/faustlibraries).
* Read the [Syntax Manual](https://faustdoc.grame.fr/manual/syntax/).

## Quick Install

### Windows

Run the latest `win64.exe` installer from FAUST's [releases](https://github.com/grame-cncm/faust/releases). After installing, copy `C:/Program Files/Faust/share/faust/` to `C:/Program Files/Derivative/TouchDesigner/share/faust/`. If you're using a TouchDesigner executable in a different location, the destination path in this step would be different such as `C:\Program Files\Derivative\TouchDesigner.2021.38110\share\faust`. If you want the absolute latest version of Faust, you can create this `share/faust` folder by copying from [Faust Libraries](https://github.com/grame-cncm/faustlibraries).

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download and unzip the latest Windows version. Copy `faust.dll`, `TD-Faust.dll`, and `sndfile.dll` to this repository's `Plugins` folder. Open `TD-Faust.toe` and compile a few examples.

### macOS

Run the latest `.dmg` installer from FAUST's [releases](https://github.com/grame-cncm/faust/releases). If you have an M1 ("Apple Silicon"), choose `*arm64.dmg`, otherwise choose `*x64.dmg`. After installing, copy `Faust-2.X/share/faust/` to `/usr/local/share/faust`. If you want the absolute latest version of Faust, you can create this `share/faust` folder by copying from [Faust Libraries](https://github.com/grame-cncm/faustlibraries).

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download and unzip the latest macOS version. Copy `libfaust.2.dylib` and `TD-Faust.plugin` to this repository's `Plugins` folder. Open `TD-Faust.toe` and compile a few examples.

If there's a warning about the codesigning certificate, you may need to compile TD-Faust on your own computer.

1. Clone this repository with git. Then update all submodules in the root of the repository with `git submodule update --init --recursive`
2. Install Xcode.
3. [Install CMake](https://cmake.org/download/) and confirm that it's installed by running `cmake --version` in Terminal.
4. Find your Development Profile. Open Keychain Access, go to 'login' on the left, and look for something like `Apple Development: example@example.com (ABCDE12345)`. Then in Terminal, run `export CODESIGN_IDENTITY="Apple Development: example@example.com (ABCDE12345)"` with your own info substituted. If you weren't able to find your profile, you need to create one. Open Xcode, go to "Accounts", add your Apple ID, click "Manage Certificates", and use the plus icon to add a profile. Then check Keychain Access again.
5. In the same Terminal window, navigate to the root of this repository and run `sh build_macos.sh`
6. Open `TD-Faust.toe`

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
* Setup UI: See below.
* Reset: Clear the compiled code, if there is any.
* Clear MIDI: Clear the MIDI notes (in case something went wrong).
* Viewer COMP: The [Container COMP](https://docs.derivative.ca/Container_COMP) which will be used when `Setup UI` is pulsed.

### Setup UI

One great feature of TD-Faust is that user interfaces that appear in the Faust code can become [Custom Parameters](https://docs.derivative.ca/Custom_Parameters) by pressing the "Setup UI" button. Take a look at the simple Faust code below:

```faust
import("stdfaust.lib");
volume = hslider("Volume", 1., 0., 1., ma.EPSILON);
process = os.osc(440.)*volume <: _, _;
```

After compiling this code, press the `Setup UI` button to build a UI in the `Viewer COMP`. The Faust base will create a secondary page of custom parameters titled "Control", and because of the code we've written there will be one custom Float parameter named "Volume". Setting up the UI like this works by saving an XML file inside a directory called `dsp_output`. It will also print out information inside the TouchDesigner console. On your operating system, you should set the environment variable `TOUCH_TEXT_CONSOLE` to 1. Then restart TouchDesigner and you'll start seeing the text console window. In a *non-polyphonic example*, this is an example of the important printout section:

<details>
<summary>non-polyphonic example</summary>
<pre>
<code>
---------------- DUMPING [Faust] PARAMETERS ---------------
/Pitch_Shifter/shift_semitones : 3
/Pitch_Shifter/window_samples : 3
/Pitch_Shifter/xfade_samples : 3
Number of Inputs: 2
Number of Outputs: 2
</code>
</pre>
</details>

This means that you can pass a CHOP containing those three parameter names to the second input of the Faust CHOP. You can even make this CHOP have the same sample rate as the Faust CHOP in order to have no-latency control of the parameters.

In a *polyphonic* example with `Group Voices` enabled, this is an example of the important printout section:

<details>
<summary>polyphonic example</summary>
<pre>
<code>
---------------- DUMPING [Faust] PARAMETERS ---------------
/Sequencer/DSP1/Polyphonic/Voices/Panic : 0
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/cutoff : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/cutoff_modulation : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/A : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/D : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/R : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/S : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/A : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/D : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/R : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/S : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/freq : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/gate : 0
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/note_offset : 3
Number of Inputs: 0
Number of Outputs: 2
</code>
</pre>
</details>

Like the non-polyphonic example above, this indicates that you can control the `cutoff`, `cutoff_modulation`, and other parameters with a wired input CHOP with the correct channel names. Importantly, the same values will change all the voices simultaneously.

If `Group Voices` is disabled, the printout will look like this:

<details>
<summary>grouped-voices polyphonic example</summary>
<pre>
<code>
---------------- DUMPING [Faust] PARAMETERS ---------------
/Sequencer/DSP1/Polyphonic/Voices/Panic : 0
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/cutoff : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/cutoff_modulation : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/A : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/D : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/R : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env0/S : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/A : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/D : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/R : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/env1/S : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/freq : 3
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/gate : 0
/Sequencer/DSP1/Polyphonic/Voices/MyInstrument/note_offset : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/cutoff : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/cutoff_modulation : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env0/A : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env0/D : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env0/R : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env0/S : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env1/A : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env1/D : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env1/R : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/env1/S : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/freq : 3
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/gate : 0
/Sequencer/DSP1/Polyphonic/Voice1/MyInstrument/note_offset : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/cutoff : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/cutoff_modulation : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env0/A : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env0/D : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env0/R : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env0/S : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env1/A : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env1/D : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env1/R : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/env1/S : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/freq : 3
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/gate : 0
/Sequencer/DSP1/Polyphonic/Voice2/MyInstrument/note_offset : 3
Number of Inputs: 0
Number of Outputs: 2
</code>
</pre>
</details>

Note how there is a set of parameters for each voice. All parameters can be addressed individually with the input CHOP.

### Group Voices and Dynamic Voices

The `Group Voices` and `Dynamic Voices` toggles matter when using [polyphony](https://faustdoc.grame.fr/manual/midi/). You should also read the `Setup UI` section above.

If you enable `Group Voices`, one set of parameters will control all voices at once. Otherwise, you will need to address a set of parameters for each voice.

If you enable `Dynamic Voices`, then voices whose notes have been released will be dynamically turned off in order to save computation. Dynamic Voices should be on in most cases such as when you're wiring a MIDI buffer as the third input to the Faust CHOP. There is a special case in which you might want `Dynamic Voices` off:
* You are not wiring a MIDI buffer as the third input.
* `Group Voices` is off.
* You are individually addressing the frequencies, gates and/or gains of the polyphonic voices. This step works as a replacement for the lack of the wired MIDI buffer.

### Control Rate and Sample Rate

The sample rate is typically a high number such as 44100 Hz, and the control rate of UI parameters might be only 60 Hz. This can lead to artifacts. Suppose we are listening to a 44.1 kHz signal, but we are multiplying it by a 60 Hz "control" signal such as a UI slider meant to control the volume.

```faust
import("stdfaust.lib");
volume = hslider("Volume", 1., 0., 1., ma.EPSILON);
process = os.osc(440.)*volume <: _, _;
```

In TouchDesigner, we can press "Setup UI" to get a "Volume" custom parameter on the "Control" page of the Faust base. You can look inside the base to see how the custom parameter is wired into the Faust CHOP. By default, this "Volume" signal will only be the project cook rate (60 Hz). Therefore, as you change the volume, you will hear artifacts in the output. There are two solutions:

1. Use [si.smoo](https://faustlibraries.grame.fr/libs/signals/#sismoo) or [si.smooth](https://faustlibraries.grame.fr/libs/signals/#sismooth) to smooth the control signal: `volume = hslider("Volume", 1., 0., 1., ma.EPSILON) : si.smoo;`

2. Create a higher sample-rate control signal, possibly as high as the Faust CHOP, and connect it to the Faust base.

## Licenses / Thank You

TD-Faust (GPL-Licensed) relies on these projects/softwares:

* FAUST ([GPL](https://github.com/grame-cncm/faust/blob/master/COPYING.txt)-licensed).
* [pd-faustgen](https://github.com/CICM/pd-faustgen) (MIT-Licensed) provided helpful CMake examples.
* [FaucK](https://github.com/ccrma/chugins/tree/main/Faust) (MIT-Licensed), an integration of FAUST and [ChucK](http://chuck.stanford.edu/).
* [TouchDesigner](https://derivative.ca/)
