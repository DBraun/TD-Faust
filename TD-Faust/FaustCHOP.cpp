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

#include "FaustCHOP.h"

#include <cmath>
#include <assert.h>

// general includes
#include <stdio.h>
#include <limits.h>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <fstream>
using namespace std;

#ifndef SAFE_DELETE
#define SAFE_DELETE(x)              do { if(x){ delete x; x = NULL; } } while(0)
#define SAFE_DELETE_ARRAY(x)        do { if(x){ delete [] x; x = NULL; } } while(0)
#define SAFE_RELEASE(x)             do { if(x){ x->release(); x = NULL; } } while(0)
#define SAFE_ADD_REF(x)             do { if(x){ x->add_ref(); } } while(0)
#define SAFE_REF_ASSIGN(lhs,rhs)    do { SAFE_RELEASE(lhs); (lhs) = (rhs); SAFE_ADD_REF(lhs); } while(0)
#endif

std::list<GUI*> GUI::fGuiList;
ztimedmap GUI::gTimedZoneMap;

// These functions are basic C function, which the DLL loader can find
// much easier than finding a C++ Class.
// The DLLEXPORT prefix is needed so the compile exports these functions from the .dll
// you are creating
extern "C"
{

	DLLEXPORT
		void
		FillCHOPPluginInfo(CHOP_PluginInfo* info)
	{
		// Always set this to CHOPCPlusPlusAPIVersion.
		info->apiVersion = CHOPCPlusPlusAPIVersion;

		// The opType is the unique name for this CHOP. It must start with a 
		// capital A-Z character, and all the following characters must lower case
		// or numbers (a-z, 0-9)
		info->customOPInfo.opType->setString("Faustchop");

		// The opLabel is the text that will show up in the OP Create Dialog
		info->customOPInfo.opLabel->setString("Faust CHOP");
		info->customOPInfo.opIcon->setString("FAU");

		// Information about the author of this OP
		info->customOPInfo.authorName->setString("David Braun");
		info->customOPInfo.authorEmail->setString("github.com/DBraun");

		// This CHOP can work with 0 inputs
		info->customOPInfo.minInputs = 0;
		info->customOPInfo.maxInputs = 3;
	}

	DLLEXPORT
		CHOP_CPlusPlusBase*
		CreateCHOPInstance(const OP_NodeInfo* info)
	{
		// Return a new instance of your class every time this is called.
		// It will be called once per CHOP that is using the .dll
		return new FaustCHOP(info);
	}

	DLLEXPORT
		void
		DestroyCHOPInstance(CHOP_CPlusPlusBase* instance)
	{
		// Delete the instance here, this will be called when
		// Touch is shutting down, when the CHOP using that instance is deleted, or
		// if the CHOP loads a different DLL
		delete (FaustCHOP*)instance;
	}

};


FaustCHOP::FaustCHOP(const OP_NodeInfo* info) : myNodeInfo(info)
{
	// sample rate
	m_srate = 44100.; // will be written immediately by getOutputInfo
	// clear
	m_factory = NULL;
	m_poly_factory = NULL;
	m_dsp = NULL;
	m_dsp_poly = NULL;
	m_ui = NULL;
	m_midi_ui = NULL;
	m_soundUI = NULL;
	// zero
	m_input = NULL;
	m_output = NULL;
	// default
	m_numInputChannels = 0;
	m_numOutputChannels = 0;
	// auto import
	m_autoImport = "// Faust CHOP auto import:\n \
        import(\"stdfaust.lib\");\n";

	myExecuteCount = 0;

#ifdef WIN32
	// At the start of every process
	guiUpdateMutex = CreateMutex(NULL, FALSE, L"Faust gui::update Mutex");  // todo: enable mutex on linux and macOS
#endif

	clearMIDI();
}

FaustCHOP::~FaustCHOP()
{
	// clear
	clear();
	clearBufs();
}

void
FaustCHOP::getGeneralInfo(CHOP_GeneralInfo* ginfo, const OP_Inputs* inputs, void* reserved1)
{
	// This will cause the node to cook every frame
	ginfo->cookEveryFrameIfAsked = true;

	// Note: To disable timeslicing you'll need to turn this off, as well as ensure that
	// getOutputInfo() returns true, and likely also set the info->numSamples to how many
	// samples you want to generate for this CHOP. Otherwise it'll take on length of the
	// input CHOP, which may be timesliced.
	ginfo->timeslice = true;
}

bool
FaustCHOP::getOutputInfo(CHOP_OutputInfo* info, const OP_Inputs* inputs, void* reserved1)
{
	// If there is an input connected, we are going to match it's channel names etc
	// otherwise we'll specify our own.

	info->numChannels = m_numOutputChannels;

	// Since we are outputting a timeslice, the system will dictate
	// the numSamples and startIndex of the CHOP data
	//info->numSamples = 1;
	//info->startIndex = 0

	// For illustration we are going to output 120hz data
	info->sampleRate = m_srate = inputs->getParDouble("Samplerate");

	return true;
}

void
FaustCHOP::getChannelName(int32_t index, OP_String* name, const OP_Inputs* inputs, void* reserved1)
{
	std::stringstream ss;
	ss << "chan" << (index+1);
	name->setString(ss.str().c_str());
}

void
FaustCHOP::clear()
{
	m_numInputChannels = 0;
	m_numOutputChannels = 0;

	// todo: do something with m_midi_handler
	if (m_dsp_poly) {
		m_midi_handler.removeMidiIn(m_dsp_poly);
		m_midi_handler.stopMidi();
	}
	if (m_midi_ui) {
		m_midi_ui->removeMidiIn(m_dsp_poly);
		m_midi_ui->stop();
	}

	SAFE_DELETE(m_dsp);
	SAFE_DELETE(m_ui);
	SAFE_DELETE(m_dsp_poly);
	SAFE_DELETE(m_midi_ui);
	SAFE_DELETE(m_soundUI);

	//deleteAllDSPFactories();  // don't actually do this!!
	deleteDSPFactory(m_factory);
	//deleteDSPFactory(m_poly_factory);
	m_poly_factory = NULL;
	m_factory = NULL;

	clearMIDI();
}

void
FaustCHOP::clearMIDI()
{
	for (int i = 0; i < 127; i++) {
		m_midiBuffer[i] = 0;
	}

	if (m_dsp_poly) {
		m_dsp_poly->instanceClear();
	}
}

void
FaustCHOP::clearBufs()
{
	if (m_input != NULL) {
		for (int i = 0; i < m_numInputChannels; i++) {
			SAFE_DELETE_ARRAY(m_input[i]);
		}
	}
	if (m_output != NULL) {
		for (int i = 0; i < m_numOutputChannels; i++) {
			SAFE_DELETE_ARRAY(m_output[i]);
		}
	}
	SAFE_DELETE_ARRAY(m_input);
	SAFE_DELETE_ARRAY(m_output);
}

void
FaustCHOP::allocate(int inputChannels, int outputChannels, int numSamples)
{
	// clear
	clearBufs();

	// set
	m_numInputChannels = min(inputChannels, MAX_INPUTS);
	m_numOutputChannels = min(outputChannels, MAX_OUTPUTS);

	// allocate channels
	m_input =  new FAUSTFLOAT * [m_numInputChannels];
	m_output = new FAUSTFLOAT * [m_numOutputChannels];
	m_allocatedSamples = numSamples;
	// allocate buffers for each channel
	for (int chan = 0; chan < m_numInputChannels; chan++) {
		// single sample for each
		m_input[chan] = new FAUSTFLOAT[numSamples];
	}
	for (int chan = 0; chan < m_numOutputChannels; chan++) {
		// single sample for each
		m_output[chan] = new FAUSTFLOAT[numSamples];
	}
}

#define FAUSTPROCESSOR_FAIL_COMPILE clear(); return false;

bool
FaustCHOP::eval(const string& code)
{
	// clean up
	clear();

	// arguments
	int argc = 0;
	const char** argv;
	if (strcmp(m_faustLibrariesPath, "") != 0) {
		argc = 2;
		argv = new const char* [argc];
		argv[0] = "-I";
		argv[1] = m_faustLibrariesPath;
	}
	else {
		argv = new const char* [argc];
	}

	// optimization level
	const int optimize = -1;

	// save
	m_code = code;

	// auto import
	const string theCode = m_autoImport + "\n" + code;

	// create new factory
	if (m_polyphony_enable) {
		m_poly_factory = createPolyDSPFactoryFromString("my_dsp", theCode,
			argc, argv, "", m_errorString, optimize);
	}
	else {
		m_factory = createDSPFactoryFromString("my_dsp", theCode,
			argc, argv, "", m_errorString, optimize);
	}

	if (argv) {
		for (int i = 0; i < argc; i++) {
			argv[i] = NULL;
		}
		argv = NULL;
	}

	// check for error
	if (strcmp(m_errorString.c_str(), "") != 0) {
		// output error
		cerr << "[Faust]: " << m_errorString << endl;
		FAUSTPROCESSOR_FAIL_COMPILE
	}

	//// print where faustlib is looking for stdfaust.lib and the other lib files.
	//auto pathnames = m_factory->getIncludePathnames();
	//cout << "pathnames:\n" << endl;
	//for (auto name : pathnames) {
	//	cout << name << "\n" << endl;
	//}
	//cout << "library list:\n" << endl;
	//auto librarylist = m_factory->getLibraryList();
	//for (auto name : librarylist) {
	//	cout << name << "\n" << endl;
	//}

	if (m_midi_enable) {
		m_midi_handler = rt_midi("my_midi");
	}

	if (m_polyphony_enable) {
		bool doDynamicallyAllocateVoices = false;
		m_dsp_poly = m_poly_factory->createPolyDSPInstance(m_nvoices, doDynamicallyAllocateVoices, m_groupVoices);
		if (!m_dsp_poly) {
			std::cerr << "Cannot create instance " << std::endl;
			FAUSTPROCESSOR_FAIL_COMPILE
		}
		if (m_midi_enable) {
			m_midi_handler.addMidiIn(m_dsp_poly);
		}
	} else {
		// create DSP instance
		m_dsp = m_factory->createDSPInstance();
		if (!m_dsp) {
			std::cerr << "Cannot create instance " << std::endl;
			FAUSTPROCESSOR_FAIL_COMPILE
		}
	}

	dsp* theDsp = m_polyphony_enable ? m_dsp_poly : m_dsp;

	// make new UI
	if (m_midi_enable)
	{
		m_midi_ui = new MidiUI(&m_midi_handler);
		theDsp->buildUserInterface(m_midi_ui);
	}

	// build ui
	m_ui = new FaustCHOPUI();
	theDsp->buildUserInterface(m_ui);

	// build sound ui
	if (strcmp(m_assetsDirPath, "") != 0) {
		m_soundUI = new SoundUI(m_assetsDirPath, m_srate);
		theDsp->buildUserInterface(m_soundUI);
	}

	// get channels
	int inputs = theDsp->getNumInputs();
	int outputs = theDsp->getNumOutputs();

	// see if we need to alloc
	if (inputs != m_numInputChannels || outputs != m_numOutputChannels) {
		// clear and allocate
		allocate(inputs, outputs, 1);
	}

	// init
	theDsp->init((int)(m_srate + .5));

	if (m_midi_enable) {
		m_midi_ui->run();
	}

	return true;
}

bool
FaustCHOP::compile(const string& path)
{
	// open file
	ifstream fin(path.c_str());
	// check
	if (!fin.good())
	{
		// error
		cerr << "[Faust]: ERROR opening file: '" << path << "'" << endl;
		return false;
	}

	// clear code string
	m_code = "";
	// get it
	for (string line; std::getline(fin, line); ) {
		m_code += line + '\n';
	}
	// eval it
	return eval(m_code);
}

bool
FaustCHOP::compile()
{
	return eval(m_code);
}


void
FaustCHOP::setup_touchdesigner_ui()
{
	if (m_errorString.empty()) {
		if (m_ui) {
			cerr << "---------------- DUMPING [Faust] PARAMETERS ---------------" << endl;
			m_ui->dumpParams();
			cerr << "Number of Inputs: " << m_numInputChannels << endl;
			cerr << "Number of Outputs: " << m_numOutputChannels << endl;
			cerr << "-----------------------------------------------------------" << endl;
		}

		const string theCode = m_autoImport + "\n" + m_code;

		// arguments
		int argc = 1;		
		const char** argv = new const char* [argc];
		argv[0] = "-xml";
		if (strcmp(m_faustLibrariesPath, "") != 0) {
			argc = 3;
			argv = new const char* [argc];
			argv[0] = "-xml";
			argv[1] = "-I";
			argv[2] = m_faustLibrariesPath;
		}

		// This saves to an XML file on disk (undesirable side-effect).
		// It would be better to get it to a variable.
		string myError;
		generateAuxFilesFromString(string("my_dsp"), theCode, argc, argv, myError);

		cerr << myError.c_str() << endl;
	}
	else {
		cerr << "[Faust]: " << m_errorString << endl;
	}
}

float
FaustCHOP::setParam(const string& n, float p)
{
	// sanity check
	if (!m_ui) return 0;

	// set the value
	m_ui->setParamValue(n.c_str(), p);

	return p;
}

float
FaustCHOP::getParam(const string& n)
{
	if (!m_ui) return 0; // todo: better handling
	return m_ui->getParamValue(n.c_str());
}

string
FaustCHOP::code()
{
	return m_code;
}

void
FaustCHOP::execute(CHOP_Output* output,
	const OP_Inputs* inputs,
	void* reserved)
{
	myExecuteCount++;

	const OP_DATInput* dat = inputs->getParDAT("Code");
	if (dat) {
		m_code = std::string(dat->getCell(0, 0));
	}

	m_faustLibrariesPath = inputs->getParString("Faustlibrariespath");
	m_assetsDirPath = inputs->getParString("Assetspath");

	m_nvoices = inputs->getParInt("Nvoices");
	m_midi_enable = inputs->getParDouble("Midi");
	m_polyphony_enable = inputs->getParDouble("Polyphony");
	m_groupVoices = inputs->getParInt("Groupvoices");

	if ((m_numOutputChannels != output->numChannels) || output->numChannels == 0) {
		return;
	}

	const OP_CHOPInput* audioInput = inputs->getInputCHOP(0);
	const OP_CHOPInput* controlInput = inputs->getInputCHOP(1);
	const OP_CHOPInput* midiInput = inputs->getInputCHOP(2);

	int blockSize = (int) inputs->getParDouble("Blocksize");

	if (m_polyphony_enable && midiInput && m_dsp_poly)
	{
		// We have to make the block size one so that we can step through the MIDI input one at a time.
		blockSize = 1;
	}

	if (audioInput)
	{
		if (audioInput->numChannels < m_numInputChannels) {
			// todo: throw error
			return;
		}
	}

	dsp* theDsp = m_polyphony_enable ? m_dsp_poly : m_dsp;

	if (theDsp != NULL) {

		for (int i = 0; i < output->numSamples; i += blockSize) {

			if (controlInput && i < controlInput->numSamples) {
				for (int chan = 0; chan < controlInput->numChannels; chan++) {
					setParam(std::string(controlInput->getChannelName(chan)), controlInput->getChannelData(chan)[i]);
				}

				// If polyphony is enabled and we're grouping voices,
				// several voices might share the same parameters in a group.
				// Therefore we have to call updateAllGuis to update all dependent parameters.
				if (m_nvoices > 0 && m_polyphony_enable && m_groupVoices) {
#ifdef WIN32
					// When you want to access shared memory:
					DWORD dwWaitResult = WaitForSingleObject(guiUpdateMutex, INFINITE);

					if (dwWaitResult == WAIT_OBJECT_0 || dwWaitResult == WAIT_ABANDONED)
					{
						if (dwWaitResult == WAIT_ABANDONED)
						{
							// todo:
							// Shared memory is maybe in inconsistent state because other program
							// crashed while holding the mutex. Check the memory for consistency
						}

						// Have Faust update all GUIs.
						GUI::updateAllGuis();

						// After this line other processes can access shared memory
						ReleaseMutex(guiUpdateMutex);
					}
#else
					GUI::updateAllGuis(); // todo: enable mutex on linux and macOS
#endif
				}

			}

			int numSamples = min(output->numSamples - i, blockSize);

			if (numSamples != m_allocatedSamples) {
				allocate(m_numInputChannels, m_numOutputChannels, numSamples);
			}

			if (midiInput && m_polyphony_enable && m_dsp_poly && (i < midiInput->numSamples)) {

				for (int pitch = 0; pitch < std::min(127, midiInput->numChannels); pitch++) {

					int velo = int(127 * midiInput->getChannelData(pitch)[i]);

					int pastVel = m_midiBuffer[pitch];

					if (pastVel != velo) {

						if (velo > 0 && pastVel <= 0) {
							m_dsp_poly->keyOn(0, pitch, velo);
						}
						else if (velo <= 0 && pastVel > 0) {
							m_dsp_poly->keyOff(0, pitch, velo);
						}

						m_midiBuffer[pitch] = velo;
					}

				}
			}

			if (audioInput) {
				for (int chan = 0; chan < m_numInputChannels; chan++)
					// Make sure we don't read past the end of the CHOP input
					for (int samp = 0; samp < numSamples && (i+samp) < audioInput->numSamples; samp++) {
					{						
						m_input[chan][samp] = audioInput->getChannelData(chan)[i+samp];
					}
				}
			}

			theDsp->compute(numSamples, m_input, m_output);

			for (int chan = 0; chan < output->numChannels; chan++) {
				for (int samp = 0; samp < numSamples; samp++) {
					output->channels[chan][i + samp] = m_output[chan][samp];
				}
			}
		}
	}
}

int32_t
FaustCHOP::getNumInfoCHOPChans(void* reserved1)
{
	// We return the number of channel we want to output to any Info CHOP
	// connected to the CHOP. In this example we are just going to send one channel.
	return 1;
}

void
FaustCHOP::getInfoCHOPChan(int32_t index,
	OP_InfoCHOPChan* chan,
	void* reserved1)
{
	// This function will be called once for each channel we said we'd want to return
	// In this example it'll only be called once.

	if (index == 0)
	{
		chan->name->setString("executeCount");
		chan->value = (float)myExecuteCount;
	}
}

bool
FaustCHOP::getInfoDATSize(OP_InfoDATSize* infoSize, void* reserved1)
{
	infoSize->rows = 1;
	infoSize->cols = 2;
	// Setting this to false means we'll be assigning values to the table
	// one row at a time. True means we'll do it one column at a time.
	infoSize->byColumn = false;
	return true;
}

void
FaustCHOP::getInfoDATEntries(int32_t index,
	int32_t nEntries,
	OP_InfoDATEntries* entries,
	void* reserved1)
{
	char tempBuffer[4096];

	if (index == 0)
	{
		// Set the value for the first column
		entries->values[0]->setString("executeCount");

		// Set the value for the second column
#ifdef _WIN32
		sprintf_s(tempBuffer, "%d", myExecuteCount);
#else // macOS
		snprintf(tempBuffer, sizeof(tempBuffer), "%d", myExecuteCount);
#endif
		entries->values[1]->setString(tempBuffer);
	}
}

void
FaustCHOP::setupParameters(OP_ParameterManager* manager, void* reserved1)
{

	// Sample Rate
	{
		OP_NumericParameter	np;

		np.name = "Samplerate";
		np.label = "Sample Rate";
		np.defaultValues[0] = 44100.0;
		np.minSliders[0] = 0.0;
		np.maxSliders[0] = 96000.0;

		OP_ParAppendResult res = manager->appendFloat(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Buffer Size
	{
		OP_NumericParameter	np;

		np.name = "Blocksize";
		np.label = "Block Size";
		np.defaultValues[0] = 512.;
		np.minSliders[0] = 1.;
		np.maxSliders[0] = 1024.0;

		OP_ParAppendResult res = manager->appendFloat(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Polyphony disable/enable
	{
		OP_NumericParameter	np;

		np.name = "Polyphony";
		np.label = "Polyphony";
		np.defaultValues[0] = 1.;

		OP_ParAppendResult res = manager->appendToggle(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Polyphony N Voices
	{
		OP_NumericParameter	np;
		np.name = "Nvoices";
		np.label = "N Voices";
		np.defaultValues[0] = 4.;
		np.minSliders[0] = 1.;
		np.maxSliders[0] = 16.;
		np.clampMins[0] = true;
		np.clampMaxes[0] = true;
		np.maxValues[0] = 512.;
		np.minValues[0] = 1.;

		OP_ParAppendResult res = manager->appendInt(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Midi disable/enable
	{
		OP_NumericParameter	np;

		np.name = "Midi";
		np.label = "MIDI";
		np.defaultValues[0] = 1.;

		OP_ParAppendResult res = manager->appendToggle(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Group voices
	{
		OP_NumericParameter	np;

		np.name = "Groupvoices";
		np.label = "Group Voices";
		np.defaultValues[0] = 1.;

		OP_ParAppendResult res = manager->appendToggle(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// chuck source code DAT
	{
		OP_StringParameter	sp;

		sp.name = "Code";
		sp.label = "Code";

		sp.defaultValue = "";

		OP_ParAppendResult res = manager->appendDAT(sp);
		assert(res == OP_ParAppendResult::Success);
	}

	// Faust libraries path
	{
		OP_NumericParameter	np;
		OP_StringParameter sp;

		sp.name = "Faustlibrariespath";
		sp.label = "Faust Libraries Path";

		OP_ParAppendResult res = manager->appendString(sp);
		assert(res == OP_ParAppendResult::Success);
	}

	// assets folder path
	{
		OP_NumericParameter	np;
		OP_StringParameter sp;

		sp.name = "Assetspath";
		sp.label = "Assets Path";

		OP_ParAppendResult res = manager->appendString(sp);
		assert(res == OP_ParAppendResult::Success);
	}

	// Compile
	{
		OP_NumericParameter	np;

		np.name = "Compile";
		np.label = "Compile";

		OP_ParAppendResult res = manager->appendPulse(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Save UI
	{
		OP_NumericParameter	np;

		np.name = "Setupuipulse";
		np.label = "Setup UI";

		OP_ParAppendResult res = manager->appendPulse(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Reset
	{
		OP_NumericParameter	np;

		np.name = "Reset";
		np.label = "Reset";

		OP_ParAppendResult res = manager->appendPulse(np);
		assert(res == OP_ParAppendResult::Success);
	}

	// Clear MIDI
	{
		OP_NumericParameter	np;

		np.name = "Clearmidi";
		np.label = "Clear MIDI";

		OP_ParAppendResult res = manager->appendPulse(np);
		assert(res == OP_ParAppendResult::Success);
	}

	//// menu parameter example
	//{
	//	OP_StringParameter	sp;

	//	sp.name = "Shape";
	//	sp.label = "Shape";

	//	sp.defaultValue = "Sine";

	//	const char *names[] = { "Sine", "Square", "Ramp" };
	//	const char *labels[] = { "Sine", "Square", "Ramp" };

	//	OP_ParAppendResult res = manager->appendMenu(sp, 3, names, labels);
	//	assert(res == OP_ParAppendResult::Success);
	//}
}

void
FaustCHOP::pulsePressed(const char* name, void* reserved1)
{

	if (!strcmp(name, "Compile"))
	{
		compile();
	}

	if (!strcmp(name, "Reset"))
	{
		clear();
	}

	if (!strcmp(name, "Clearmidi"))
	{
		clearMIDI();
	}

	if (!strcmp(name, "Setupuipulse"))
	{
		setup_touchdesigner_ui();
	}
}
