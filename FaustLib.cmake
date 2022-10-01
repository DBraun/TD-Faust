# This file was adapted from https://github.com/CICM/pd-faustgen and therefore includes
# the following license:

# MIT License

# Copyright (c) 2018 Pierre Guillot

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

## Create Faust Lib
message(STATUS "Faust Library")

## Save the llvm directory and change it for subdirectory
if(DEFINED LLVM_DIR)
  set(LLVM_DIR_TEMP   ${LLVM_DIR})
  set(LLVM_DIR        "./../.${LLVM_DIR_TEMP}")
endif()

## Hardcoded targets for faust
## NB: In order to build the dynamic library, you need to build the exectuable library.
## See faust/build/CMakeLists.txt for more context
set(MSVC_STATIC         OFF CACHE STRING  "Use static runtimes with MSVC" FORCE)
set(INCLUDE_STATIC      OFF CACHE STRING  "Include static library"        FORCE)
set(INCLUDE_EXECUTABLE  ON  CACHE STRING  "Include runtime executable"    FORCE)
set(INCLUDE_DYNAMIC     ON  CACHE STRING  "Include dynamic library"       FORCE)
set(INCLUDE_OSC         OFF CACHE STRING  "Include Faust OSC library"     FORCE)
set(INCLUDE_HTTP        OFF CACHE STRING  "Include Faust HTTPD library"   FORCE)

## Hardcoded backends for faust
## NB: The CPP_BACKEND is necessary for exporting a DSP to XML and/or C++
set(ASMJS_BACKEND  OFF                       CACHE STRING  "Include ASMJS backend"       FORCE)
set(C_BACKEND      OFF                       CACHE STRING  "Include C backend"           FORCE)
set(CPP_BACKEND    DYNAMIC                   CACHE STRING  "Include CPP backend"         FORCE)
set(FIR_BACKEND    OFF                       CACHE STRING  "Include FIR backend"         FORCE)
set(INTERP_BACKEND OFF                       CACHE STRING  "Include INTERPRETER backend" FORCE)
set(JAVA_BACKEND   OFF                       CACHE STRING  "Include JAVA backend"        FORCE)
set(JS_BACKEND     OFF                       CACHE STRING  "Include JAVASCRIPT backend"  FORCE)
set(LLVM_BACKEND   COMPILER DYNAMIC          CACHE STRING  "Include LLVM backend"        FORCE)
set(OLDCPP_BACKEND OFF                       CACHE STRING  "Include old CPP backend"     FORCE)
set(RUST_BACKEND   OFF                       CACHE STRING  "Include RUST backend"        FORCE)
set(WASM_BACKEND   OFF                       CACHE STRING  "Include WASM backend"        FORCE)

## Call the faust cmakelist.txt
add_subdirectory(./thirdparty/faust/build EXCLUDE_FROM_ALL)

target_compile_definitions(dynamiclib PUBLIC LLVM_BUILD_UNIVERSAL=1)

if(MSVC)
    set_property(TARGET dynamiclib APPEND_STRING PROPERTY COMPILE_FLAGS " /EHsc /D WIN32 -D_SCL_SECURE_NO_WARNINGS")
    set_property(TARGET dynamiclib APPEND_STRING PROPERTY LINK_FLAGS " /ignore:4099 ")
else()

########## <SndFile>
include (CMakeFindDependencyMacro)
if (!WIN32)
	list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/libsndfile/cmake)
endif()
find_package(SndFile REQUIRED)
target_link_libraries(dynamiclib PUBLIC SndFile::sndfile)
########## </SndFile>

include(FindCurses)

## Link the Pure Data external with llvm
find_package(LLVM REQUIRED CONFIG)
message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")
add_definitions(${LLVM_DEFINITIONS})

execute_process(COMMAND ${LLVM_DIR_TEMP}/../../../bin/llvm-config --libs all
                OUTPUT_VARIABLE llvm_components)
## If you're seeing linker errors, uncomment this message line and 
## make sure it's printing many paths to .lib files.
message(llvm_components: ${llvm_components})
string(STRIP "${llvm_components}" llvm_components)
include_directories(${LLVM_INCLUDE_DIRS})
message("LLVM_INCLUDE_DIRS: " ${LLVM_INCLUDE_DIRS})
target_link_directories(dynamiclib PRIVATE "${LLVM_INCLUDE_DIRS}/../lib")
target_link_libraries(dynamiclib PRIVATE "${llvm_components}" ${CURSES_LIBRARIES})
endif()

if(MSVC)
FILE(GLOB llvm_components ${LLVM_DIR}/../../../Release/lib/*.lib)

# Todo: why does this one need to be excluded?
list(FILTER llvm_components EXCLUDE REGEX ".*LLVM-C\.lib")

## Make sure it's printing many paths to .lib files.
message(llvm_components: ${llvm_components})
string(STRIP "${llvm_components}" llvm_components)
target_link_libraries(dynamiclib PRIVATE ${llvm_components})
endif()

## Restore llvm directory
if(DEFINED LLVM_DIR)
  set(LLVM_DIR ${LLVM_DIR_TEMP})
endif()
