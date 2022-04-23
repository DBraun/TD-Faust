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

#include <regex>

using namespace std;

//-----------------------------------------------------------------------------
// name: class FaustCHOPUI
// desc: Faust CHOP UI -> map of complete hierarchical path and zones
//-----------------------------------------------------------------------------
class FaustCHOPUI : public APIUI
{

public:

    void
    addParameter(const char* label,
        FAUSTFLOAT* zone,
        FAUSTFLOAT init,
        FAUSTFLOAT min,
        FAUSTFLOAT max,
        FAUSTFLOAT step,
        ItemType type) {

        // The superclass APIUI is going to build a path based on the label,
        // but we can't create a path that's incompatible with what TouchDesigner
        // allows for CHOP names. For example, a chan can't have parentheses in it.
        // The substitutions here must be consistent with the `legal_chan_name` method
        // in script_build_ui.py

        std::string s(label);

        // remove open and closed parentheses.
        std::string safeLabel = std::regex_replace(s, std::regex("[\(\)]+"), "");

        // replace spaces with a single underscore
        safeLabel = std::regex_replace(safeLabel, std::regex("\\s+"), "_");

        APIUI::addParameter(safeLabel.c_str(),
            zone, init, min, max, step, type
            );

    }

    void openTabBox(const char* label) { pushLabel(cleanLabel(label)); }
    void openHorizontalBox(const char* label) { pushLabel(cleanLabel(label)); }
    void openVerticalBox(const char* label) { pushLabel(cleanLabel(label)); }

    std::string cleanLabel(const char* label) {

        std::string s(label);

        // remove open and closed parentheses.
        std::string safeLabel = std::regex_replace(s, std::regex("[\(\)]+"), "");

        // replace spaces with a single underscore
        safeLabel = std::regex_replace(safeLabel, std::regex("\\s+"), "_");

        return safeLabel;
    }

    void
    dumpParams() {
        // iterator
        auto iter = fItems.begin();
        // go
        for (; iter != fItems.end(); iter++)
        {
            // print
            cerr << iter->fPath << endl;
        }
    }
};
