# TD-Faust
TD-Faust is an integration of [FAUST](https://faust.grame.fr) (Functional Audio Stream) and [TouchDesigner](https://derivative.ca/).

## Overview
 
* FAUST code can be compiled "just-in-time" and run inside TouchDesigner.
* Tested on Windows and macOS.
* Up to 256 channels of input and 256 channels of output.
* Pick your own block size and sample rate.
* Support for all of the standard [FAUST libraries](https://faustlibraries.grame.fr/) including
* * High-order ambisonics
* * WAV-file playback
* * Oscillators, noises, filters, and more
* Automatically generated user interfaces of native TouchDesigner elements based on the FAUST code.
* MIDI data can be passed to FAUST via TouchDesigner CHOPs or hardware.
* Support for [polyphonic MIDI](https://faustdoc.grame.fr/manual/midi/).
* * You can address parameters of individual voices (like [MPE](https://en.wikipedia.org/wiki/MIDI#MIDI_Polyphonic_Expression)) or group them together.

Demo:

[![Demo Video Screenshot](https://img.youtube.com/vi/0qi2lp_TgE0/0.jpg)](https://www.youtube.com/watch?v=0qi2lp_TgE0 "FAUST in TouchDesigner (Audio Coding Demo)")

## New to FAUST?

* Browse the suggested [Documentation and Resources](https://github.com/grame-cncm/faust#documentation-and-resources).
* Develop code in the [FAUST IDE](https://faustide.grame.fr/).
* Read Julius Smith's [Audio Signal Processing in FAUST](https://ccrma.stanford.edu/~jos/aspf/).
* Browse the [Libraries](https://faustlibraries.grame.fr/).
* Read the [Syntax Manual](https://faustdoc.grame.fr/manual/syntax/).

## Quick Install

### Windows

Run the latest `win64.exe` installer from FAUST's [releases](https://github.com/grame-cncm/faust/releases). After installing, copy the `.lib` files from `C:/Program Files/Faust/share/faust/` to `C:/Program Files/Derivative/TouchDesigner/share/faust/`.

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download `faust.dll` and `TD-Faust.dll`. Place them in this repository's `Plugins` folder.

### macOS

Run the latest `.dmg` installer from FAUST's [releases](https://github.com/grame-cncm/faust/releases). After installing, copy the `.lib` files from `Faust-2.X/share/faust/` to `/usr/local/share/faust`.

Visit TD-Faust's [Releases](https://github.com/DBraun/TD-Faust/releases) page. Download `libfaust.2.dylib` and `TD-Faust.plugin`. Place them in this repository's `Plugins` folder.

## Tutorial

### Writing Code

You don't need to `import("stdfaust.lib");` in the FAUST dsp code. This line is automatically added for convenience.

### Custom Parameters in TouchDesigner

* Sample Rate: Audio sample rate (such as 44100 or 48000).
* Block Size: The buffer size at which TouchDesigner tells Faust to compute. A good choice is the audio rate divided by the frame rate such as (44100/60=735). If you want to pass control parameters from TouchDesigner to Faust via a wired CHOP, the block size will limit how often those parameters are updated. In an extreme case, you can consider lowering the block size down to 1, but this will have some impact on performance.
* Polyphony: Toggle whether polyphony is enabled. Refer to the [Faust guide to polyphony](https://faustdoc.grame.fr/manual/midi/) and use the keywords such as `gate`, `gain`, and `freq` when writing the DSP code.
* N Voices: The number of polyphony voices.
* MIDI: Toggle whether **hardware** MIDI input is enabled. 
* MIDI In Virtual: Toggle whether **virtual** MIDI input is enabled (**macOS support only**)
* MIDI In Virtual Name: The name of the virtual MIDI input device (**macOS support only**)
* Group Voices: Toggle group voices (see below).
* Dynamic Voices: Toggle dynamic voices (see below).
* Code: The DAT containing the Faust code to use.
* Faust Libraries Path: The directory containing your custom faust libraries (`.lib` files)
* Assets Path: The directory containing your assets such as `.wav` files.
* Compile: Compile the Faust code.
* Setup UI: See below.
* Reset: Clear the compiled code, if there is any.
* Clear MIDI: Clear the MIDI notes (in case something went wrong).
* Viewer COMP: The [Container COMP](https://docs.derivative.ca/Container_COMP) which will be used when `Setup UI` is pulsed.

### Setup UI

After compiling, press the `Setup UI` button to build a UI in the `Viewer COMP`. This step will save an XML file inside a directory called `dsp_output`. It will also print out information inside the TouchDesigner console. On your operating system, you should set the environment variable `TOUCH_TEXT_CONSOLE` to 1. Then restart TouchDesigner and you'll start seeing the text console window.

In a *non-polyphonic example*, this is an example of the important printout section:

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

This means that you can pass a CHOP containing those three parameter names to the second input of the Faust CHOP. You can even make this CHOP have the same sample rate as the Faust CHOP and lower the `Block Size` to 1 in order to have no-latency control of the parameters.

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

* The `Group Voices` and `Dynamic Voices` toggles matter when using [polyphony](https://faustdoc.grame.fr/manual/midi/). You should also read the `Setup UI` section above.

If you enable `Group Voices`, one set of parameters will control all voices at once. Otherwise, you will need to address a set of parameters for each voice.

If you enable `Dynamic Voices`, then voices whose notes have been released will be dynamically turned off in order to save computation. Dynamic Voices should be on in most cases such as when you're wiring a MIDI buffer as the third input to the Faust CHOP. There is a special case in which you might want `Dynamic Voices` off:
* You are not wiring a MIDI buffer as the third input.
* `Group Voices` is off.
* You are individually addressing the frequencies, gates and/or gains of the polyphonic voices. This step works as a replacement for the lack of the wired MIDI buffer.

## Licenses / Thank You

TD-Faust (GPL-Licensed) relies on these projects/softwares:

* FAUST ([GPL](https://github.com/grame-cncm/faust/blob/master/COPYING.txt)-licensed).
* [pd-faustgen](https://github.com/CICM/pd-faustgen) (MIT-Licensed) provided helpful CMake examples.
* [FaucK](https://github.com/ccrma/chugins/tree/main/Faust) (MIT-Licensed), an integration of FAUST and [ChucK](http://chuck.stanford.edu/).
* [TouchDesigner](https://derivative.ca/)
