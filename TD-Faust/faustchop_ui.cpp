#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#include <stdint.h>
#include "GL_Extensions.h"

#define DLLEXPORT __declspec (dllexport)
#else
#include <OpenGL/gltypes.h>
#define DLLEXPORT
#endif

#include <map>
#include <iostream>

// faust include
#include "faust/dsp/llvm-dsp.h"
#include "faust/gui/UI.h"
#include "faust/gui/APIUI.h"
#include "faust/gui/PathBuilder.h"

using namespace std;

//-----------------------------------------------------------------------------
// name: class FaustCHOPUI
// desc: Faust CHOP UI -> map of complete hierarchical path and zones
//-----------------------------------------------------------------------------
class FaustCHOPUI : public APIUI
{

public:

    void dumpParams()
    {
        // iterator
        std::map<std::string, int>::iterator iter = fPathMap.begin();
        // go
        for (; iter != fPathMap.end(); iter++)
        {
            // print
            cerr << iter->first << " : " << (iter->second) << endl;
        }
    }
};