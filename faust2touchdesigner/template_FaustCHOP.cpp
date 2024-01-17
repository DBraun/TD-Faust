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

#include "Faust_{OP_TYPE}_CHOP.h"

// general includes
#include <assert.h>
#include <limits.h>
#include <stdio.h>

#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;

#ifndef SAFE_DELETE
#define SAFE_DELETE(x) \
  do {                 \
    if (x) {           \
      delete x;        \
      x = NULL;        \
    }                  \
  } while (0)
#define SAFE_DELETE_ARRAY(x) \
  do {                       \
    if (x) {                 \
      delete[] x;            \
      x = NULL;              \
    }                        \
  } while (0)
#endif

// These functions are basic C function, which the DLL loader can find
// much easier than finding a C++ Class.
// The DLLEXPORT prefix is needed so the compile exports these functions from
// the .dll you are creating
extern "C" {

DLLEXPORT
void FillCHOPPluginInfo(CHOP_PluginInfo* info) {
  // Always set this to CHOPCPlusPlusAPIVersion.
  info->apiVersion = CHOPCPlusPlusAPIVersion;

  // The opType is the unique name for this CHOP. It must start with a
  // capital A-Z character, and all the following characters must lower case
  // or numbers (a-z, 0-9)
  info->customOPInfo.opType->setString("{OP_TYPE}");

  // The opLabel is the text that will show up in the OP Create Dialog
  info->customOPInfo.opLabel->setString("{OP_LABEL}");
  info->customOPInfo.opIcon->setString("{OP_ICON}");

  // Information about the author of this OP
  info->customOPInfo.authorName->setString("{AUTHOR_NAME}");
  info->customOPInfo.authorEmail->setString("{AUTHOR_EMAIL}");

  info->customOPInfo.minInputs = 0;
  info->customOPInfo.maxInputs = 1;

  // info->customOPInfo.pythonVersion->setString(PY_VERSION);
  // info->customOPInfo.pythonMethods = methods;
  //  info->customOPInfo.pythonGetSets = getSets; // todo:
}

DLLEXPORT
CHOP_CPlusPlusBase* CreateCHOPInstance(const OP_NodeInfo* info) {
  // Return a new instance of your class every time this is called.
  // It will be called once per CHOP that is using the .dll
  return new FaustCHOP(info);
}

DLLEXPORT
void DestroyCHOPInstance(CHOP_CPlusPlusBase* instance) {
  // Delete the instance here, this will be called when
  // Touch is shutting down, when the CHOP using that instance is deleted, or
  // if the CHOP loads a different DLL
  delete (FaustCHOP*)instance;
}
};

FaustCHOP::FaustCHOP(const OP_NodeInfo* info) : m_NodeInfo(info) {
  // sample rate
  m_srate = 44100.;  // will be written immediately by getOutputInfo

  m_dsp.init(m_srate);
  m_dsp.buildUserInterface(&m_ui);  // todo:

  // zero
  m_input = NULL;
  m_output = NULL;
  // default
  m_numInputChannels = m_dsp.getNumInputs();
  m_numOutputChannels = m_dsp.getNumOutputs();

  this->allocate(m_numInputChannels, m_numOutputChannels, m_blockSize);
}

FaustCHOP::~FaustCHOP() {
  clearBufs();
}

void FaustCHOP::getGeneralInfo(CHOP_GeneralInfo* ginfo, const OP_Inputs* inputs,
                               void* reserved1) {
  // This will cause the node to cook every frame
  ginfo->cookEveryFrameIfAsked = true;

  // Note: To disable timeslicing you'll need to turn this off, as well as
  // ensure that getOutputInfo() returns true, and likely also set the
  // info->numSamples to how many samples you want to generate for this CHOP.
  // Otherwise it'll take on length of the input CHOP, which may be timesliced.
  ginfo->timeslice = true;
}

bool FaustCHOP::getOutputInfo(CHOP_OutputInfo* info, const OP_Inputs* inputs,
                              void* reserved1) {
  // If there is an input connected, we are going to match it's channel names
  // etc otherwise we'll specify our own.

  info->numChannels = m_numOutputChannels;

  // Since we are outputting a timeslice, the system will dictate
  // the numSamples and startIndex of the CHOP data
  // info->numSamples = 1;
  // info->startIndex = 0

  info->sampleRate = std::max(1., inputs->getParDouble("Samplerate"));

  bool needRecompile = m_srate != info->sampleRate;
  m_srate = info->sampleRate;

  if (needRecompile) {
    m_dsp.init(m_srate);
    m_dsp.buildUserInterface(&m_ui);
  }

  return true;
}

void FaustCHOP::getChannelName(int32_t index, OP_String* name,
                               const OP_Inputs* inputs, void* reserved1) {
  std::stringstream ss;
  ss << "chan" << (index + 1);
  name->setString(ss.str().c_str());
}

void FaustCHOP::clearBufs() {
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

  m_allocatedSamples = 0;
}

void FaustCHOP::allocate(int inputChannels, int outputChannels,
                         int numSamples) {
  // clear
  clearBufs();

  // set
  m_numInputChannels = min(inputChannels, MAX_INPUTS);
  m_numOutputChannels = min(outputChannels, MAX_OUTPUTS);

  // allocate channels
  m_input = new FAUSTFLOAT*[m_numInputChannels];
  m_output = new FAUSTFLOAT*[m_numOutputChannels];
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

void FaustCHOP::getWarningString(OP_String* warning, void* reserved1) {
  warning->setString(m_warningString.c_str());
}

void FaustCHOP::getErrorString(OP_String* error, void* reserved1) {
  error->setString(m_errorString.c_str());
}

void FaustCHOP::execute(CHOP_Output* output, const OP_Inputs* inputs,
                        void* reserved) {
  m_warningString = std::string("");

  {SET_PAR_VALUES}

  if (output->numChannels == 0 || output->numChannels != m_numOutputChannels) {
    // write zeros and return
    for (int chan = 0; chan < output->numChannels; chan++) {
      auto writePtr = output->channels[chan];
      memset(writePtr, 0, output->numSamples * sizeof(float));
    }
    return;
  }

  const OP_CHOPInput* audioInput = inputs->getInputCHOP(0);

  if (!audioInput && m_numInputChannels) {
    // write zeros and return
    for (int chan = 0; chan < output->numChannels; chan++) {
      auto writePtr = output->channels[chan];
      memset(writePtr, 0, output->numSamples * sizeof(float));
    }
    m_errorString = std::string("This plugin requires an input CHOP with " +
                      to_string(m_numInputChannels) + " channels.");
    return;
  }

  // A reasonably large block size. Code farther below will make it smaller when
  // polyphony is necessary, or the control signals are high audio rate.
  m_blockSize = 1024;

  if (m_blockSize > m_allocatedSamples) {
    allocate(m_numInputChannels, m_numOutputChannels, m_blockSize);
  }

  // if channels are expected, but the number of channels provided is less than
  // what's needed, make a warning.
  if (m_numInputChannels) {
    if (!audioInput || audioInput->numChannels < m_numInputChannels) {
      m_warningString =
          std::string("Not enough audio input channels. Expected " +
                      to_string(m_numInputChannels) + " but received " +
                      to_string(audioInput->numChannels));
    }
  }
  if (audioInput && audioInput->numChannels > m_numInputChannels) {
    m_warningString =
        std::string("Too many audio input channels: Expected " +
                    to_string(m_numInputChannels) + " but received " +
                    to_string(audioInput->numChannels));
  }

  int numSamples = 0;
  float* writePtr = nullptr;
  float* readPtr = nullptr;

  int chan = 0;

  for (int i = 0; i < output->numSamples; i += m_blockSize) {
    numSamples = min(output->numSamples - i, m_blockSize);

    if (audioInput) {
      for (chan = 0; chan < min(m_numInputChannels, audioInput->numChannels);
           chan++) {
        writePtr = m_input[chan];
        readPtr = (float*)audioInput->channelData[chan];
        readPtr += i;

        memcpy(writePtr, readPtr,
               max(0, min(numSamples, audioInput->numSamples - i)) *
                   sizeof(float));
      }
    }
    // write zero for any remaining channels
    for (; chan < m_numInputChannels; chan++) {
      writePtr = m_input[chan];
      memset(writePtr, 0, numSamples * sizeof(float));
    }

    // auto start = high_resolution_clock::now();

    m_dsp.compute(numSamples, m_input, m_output);

    // auto stop = high_resolution_clock::now();
    // m_duration = duration_cast<microseconds>(stop - start);

    for (chan = 0; chan < output->numChannels; chan++) {
      writePtr = output->channels[chan];
      writePtr += i;
      memcpy(writePtr, m_output[chan], numSamples * sizeof(float));
    }
  }
  m_errorString = std::string("");
}

int32_t FaustCHOP::getNumInfoCHOPChans(void* reserved1) {
  // We return the number of channel we want to output to any Info CHOP
  // connected to the CHOP. In this example we are just going to send one
  // channel.

  int numChans = 2;

  return numChans;
}

void FaustCHOP::getInfoCHOPChan(int32_t index, OP_InfoCHOPChan* chan,
                                void* reserved1) {
  // This function will be called once for each channel we said we'd want to
  // return In this example it'll only be called once.

  if (index == 0) {
    chan->name->setString("inputs");
    chan->value = m_numInputChannels;
  } else if (index == 1) {
    chan->name->setString("block_size");
    chan->value = m_blockSize;
  } else {
  }
}

bool FaustCHOP::getInfoDATSize(OP_InfoDATSize* infoSize, void* reserved1) {
  infoSize->rows = 0;
  infoSize->cols = 2;
  // Setting this to false means we'll be assigning values to the table
  // one row at a time. True means we'll do it one column at a time.
  infoSize->byColumn = false;
  return true;
}

void FaustCHOP::getInfoDATEntries(int32_t index, int32_t nEntries,
                                  OP_InfoDATEntries* entries, void* reserved1) {
//   char tempBuffer[4096];

//   if (index == 0) {
//     // Set the value for the first column
//     entries->values[0]->setString("foo");

//     // Set the value for the second column
// #ifdef _WIN32
//     sprintf_s(tempBuffer, "%d", foo);
// #else  // macOS
//     snprintf(tempBuffer, sizeof(tempBuffer), "%d", foo);
// #endif
//     entries->values[1]->setString(tempBuffer);
//   }
}

void FaustCHOP::setupParameters(OP_ParameterManager* manager, void* reserved1) {
  // Sample Rate
  {
    OP_NumericParameter np;

    np.name = "Samplerate";
    np.label = "Sample Rate";
    np.defaultValues[0] = 44100.0;
    np.minSliders[0] = np.minValues[0] = .001;
    np.maxSliders[0] = np.maxValues[0] = 192000.0;
    np.clampMins[0] = np.clampMaxes[0] = true;

    OP_ParAppendResult res = manager->appendFloat(np);
    assert(res == OP_ParAppendResult::Success);
  }

  {SETUP_PARAMETERS}
}

void FaustCHOP::pulsePressed(const char* name, void* reserved1) {
  // if (!strcmp(name, "Foo")) {

  // }
}
