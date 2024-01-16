#pragma once

#include <string>
#include <vector>
#include <algorithm>
#include <functional>
#include <iostream>
#include <assert.h>

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif

struct UI;
struct Meta;

#include <faust/dsp/dsp.h>
#include <faust/gui/DecoratorUI.h>
#include <faust/gui/MapUI.h>
#include <faust/gui/LayoutUI.h>
#include <faust/gui/ValueConverter.h>
#include <faust/misc.h>

<<includeIntrinsic>>

<<includeclass>>