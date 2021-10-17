/* Shared Use License: This file is owned by Derivative Inc. (Derivative)
* and can only be used, and/or modified for use, in conjunction with
* Derivative's TouchDesigner software, and only if you are a licensee who has
* accepted Derivative's TouchDesigner license or assignment agreement
* (which also govern the use of this file). You may share or redistribute
* a modified version of this file provided the following conditions are met:
*
* 1. The shared file or redistribution must retain the information set out
* above and this list of conditions.
* 2. Derivative's name (Derivative Inc.) or its trademarks may not be used
* to endorse or promote products derived from this file without specific
* prior written permission from Derivative.
*/

/*
FaustCHOP is heavily inspired by FaucK and Faust.cpp: https://github.com/ccrma/chugins/tree/main/Faust
which is MIT-Licensed.
*/

#include "CHOP_CPlusPlusBase.h"
#include <iostream>

// faust include
#include "faust/dsp/llvm-dsp.h"
#include "faust/dsp/proxy-dsp.h"
#include "faust/dsp/poly-llvm-dsp.h"
#include "faust/dsp/poly-interpreter-dsp.h"
#include "generator/libfaust.h"

#include "faust/gui/meta.h"
#include "faust/gui/FUI.h"
#include "faust/gui/MidiUI.h"
#include "faust/gui/UI.h"
#include "faust/gui/GUI.h"
#include "faust/gui/SoundUI.h"
//#include "faust/gui/httpdUI.h"
//#include "faust/gui/OSCUI.h"
//#include "faust/gui/GTKUI.h"

#include "faust/midi/rt-midi.h"
#include "faust/midi/RtMidi.cpp"

#include "faustchop_ui.cpp"

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif

#ifndef MAX_INPUTS
#define MAX_INPUTS 256
#endif
#ifndef MAX_OUTPUTS
#define MAX_OUTPUTS 256
#endif

// To get more help about these functions, look at CHOP_CPlusPlusBase.h
class FaustCHOP : public CHOP_CPlusPlusBase
{
public:
	FaustCHOP(const OP_NodeInfo* info);
	virtual ~FaustCHOP();

	virtual void		getGeneralInfo(CHOP_GeneralInfo*, const OP_Inputs*, void* ) override;
	virtual bool		getOutputInfo(CHOP_OutputInfo*, const OP_Inputs*, void*) override;
	virtual void		getChannelName(int32_t index, OP_String *name, const OP_Inputs*, void* reserved) override;

	virtual void		execute(CHOP_Output*,
								const OP_Inputs*,
								void* reserved) override;


	virtual int32_t		getNumInfoCHOPChans(void* reserved1) override;
	virtual void		getInfoCHOPChan(int index,
										OP_InfoCHOPChan* chan,
										void* reserved1) override;

	virtual bool		getInfoDATSize(OP_InfoDATSize* infoSize, void* resereved1) override;
	virtual void		getInfoDATEntries(int32_t index,
											int32_t nEntries,
											OP_InfoDATEntries* entries,
											void* reserved1) override;

	virtual void		setupParameters(OP_ParameterManager* manager, void *reserved1) override;
	virtual void		pulsePressed(const char* name, void* reserved1) override;

	void clear();
	void clearMIDI();
	void clearBufs();
	void allocate(int inputChannels, int outputChannels, int numSamples);
	bool eval(const string& code);
	bool compile(const string& path);
	bool compile();
	void setup_touchdesigner_ui();
	float setParam(const string& n, float p);
	float getParam(const string& n);
	string code();


private:

	// We don't need to store this pointer, but we do for the example.
	// The OP_NodeInfo class store information about the node that's using
	// this instance of the class (like its name).
	const OP_NodeInfo*	myNodeInfo;

	// In this example this value will be incremented each time the execute()
	// function is called, then passes back to the CHOP 
	int32_t				myExecuteCount;

	// sample rate
	float m_srate;

#ifdef WIN32
	HANDLE guiUpdateMutex; // todo: enable mutex on linux and macOS
#endif

	// code text (pre any modifications)
	string m_code;
	const char* m_faustLibrariesPath;
	const char* m_assetsDirPath;
	// llvm factory
	llvm_dsp_factory* m_factory = nullptr;
	llvm_dsp_poly_factory* m_poly_factory = nullptr;
	// faust DSP object
	dsp* m_dsp = nullptr;
	dsp_poly* m_dsp_poly = nullptr;
	// faust compiler error string
	string m_errorString;
	// auto import
	string m_autoImport;
	bool m_groupVoices = true;

	// faust input buffer
	FAUSTFLOAT** m_input = nullptr;
	FAUSTFLOAT** m_output = nullptr;
	int allocatedSize = 0;

	// input and output
	int m_numInputChannels = 0;
	int m_numOutputChannels = 0;
	int m_allocatedSamples = 0;
	int m_nvoices = 0;
	bool m_polyphony_enable = false;
	bool m_midi_enable = false;

	rt_midi m_midi_handler;

	// UI
	MidiUI* m_midi_ui = nullptr;
	FaustCHOPUI* m_ui = nullptr;
	SoundUI* m_soundUI = nullptr;

	//
	int m_midiBuffer[127]; // store velocity for each pitch
};
