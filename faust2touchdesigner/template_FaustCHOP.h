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

#include "CHOP_CPlusPlusBase.h"
using namespace TD;
#include <iostream>

//#include <chrono>
// using namespace std::chrono;

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif

#ifndef MAX_INPUTS
#define MAX_INPUTS 16384
#endif
#ifndef MAX_OUTPUTS
#define MAX_OUTPUTS 16384
#endif

#include "{OP_TYPE}.h"

#include <faust/gui/APIUI.h>

using namespace std;

// To get more help about these functions, look at CHOP_CPlusPlusBase.h
class FaustCHOP : public CHOP_CPlusPlusBase {
 public:
  FaustCHOP(const OP_NodeInfo* info);
  virtual ~FaustCHOP();

  virtual void getGeneralInfo(CHOP_GeneralInfo*, const OP_Inputs*,
                              void*) override;
  virtual bool getOutputInfo(CHOP_OutputInfo*, const OP_Inputs*,
                             void*) override;
  virtual void getChannelName(int32_t index, OP_String* name, const OP_Inputs*,
                              void* reserved) override;

  virtual void execute(CHOP_Output*, const OP_Inputs*, void* reserved) override;

  virtual int32_t getNumInfoCHOPChans(void* reserved1) override;
  virtual void getInfoCHOPChan(int32_t index, OP_InfoCHOPChan* chan,
                               void* reserved1) override;

  virtual bool getInfoDATSize(OP_InfoDATSize* infoSize,
                              void* resereved1) override;
  virtual void getInfoDATEntries(int32_t index, int32_t nEntries,
                                 OP_InfoDATEntries* entries,
                                 void* reserved1) override;

  virtual void getWarningString(OP_String* warning, void* reserved1) override;
  virtual void getErrorString(OP_String* error, void* reserved1) override;

  virtual void setupParameters(OP_ParameterManager* manager,
                               void* reserved1) override;
  virtual void pulsePressed(const char* name, void* reserved1) override;

  void clearBufs();
  void allocate(int inputChannels, int outputChannels, int numSamples);

 private:
  // We don't need to store this pointer, but we do for the example.
  // The OP_NodeInfo class store information about the node that's using
  // this instance of the class (like its name).
  const OP_NodeInfo* m_NodeInfo;

  // sample rate
  float m_srate = 44100.;

  // faust compiler error string
  string m_errorString = string("");
  string m_warningString = string("");
  string m_name_app = string("");

  // buffers
  FAUSTFLOAT** m_input = nullptr;
  FAUSTFLOAT** m_output = nullptr;

  // input and output
  int m_numInputChannels = 0;
  int m_numOutputChannels = 0;
  int m_allocatedSamples = 0;

  // microseconds m_duration;

  // diagnostic vars:
  int m_blockSize = 0;

  FaustDSP m_dsp;

  APIUI m_ui;
};
