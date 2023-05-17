cmake_minimum_required(VERSION 3.13.0 FATAL_ERROR)

set(VERSION 0.4.1)
project(TD-Faust VERSION ${VERSION})

set(SndFile_DIR ${SndFile_DIR})

message(STATUS "TD-Faust external")

set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT TD-Faust)

set(TOUCHDESIGNER_INC ${PROJECT_SOURCE_DIR}/thirdparty/TouchDesigner/)

set(Headers
    "${TOUCHDESIGNER_INC}/CHOP_CPlusPlusBase.h"
    "${TOUCHDESIGNER_INC}/CPlusPlus_Common.h"
    "${TOUCHDESIGNER_INC}/GL_Extensions.h"
    "${PROJECT_SOURCE_DIR}/TD-Faust/FaustCHOP.h"
)
source_group("Headers" FILES ${Headers})

set(Sources
    "${PROJECT_SOURCE_DIR}/TD-Faust/FaustCHOP.cpp"
    "${PROJECT_SOURCE_DIR}/TD-Faust/faustchop_ui.cpp"
)

source_group("Sources" FILES ${Sources})

set(ALL_FILES
    ${Headers}
    ${Sources}
)

add_library(TD-Faust MODULE ${ALL_FILES})

set(ROOT_NAMESPACE ${PROJECT_NAME})

set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    OUTPUT_DIRECTORY_DEBUG   "${CMAKE_SOURCE_DIR}/$<CONFIG>/"
    OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/$<CONFIG>/"
    INTERPROCEDURAL_OPTIMIZATION_RELEASE "TRUE"
    BUNDLE true
    BUNDLE_EXTENSION "plugin"
    PRODUCT_BUNDLE_IDENTIFIER design.dirt.cpp.${PROJECT_NAME}
    MACOSX_BUNDLE_GUI_IDENTIFIER design.dirt.cpp.${PROJECT_NAME}
    MACOSX_BUNDLE_INFO_STRING ${PROJECT_NAME}
    MACOSX_BUNDLE_BUNDLE_NAME ${PROJECT_NAME}
    MACOSX_BUNDLE_BUNDLE_VERSION "${VERSION}"
    MACOSX_BUNDLE_SHORT_VERSION_STRING "${VERSION}"
    MACOSX_BUNDLE_COPYRIGHT "David Braun"
    MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_SOURCE_DIR}/TD-Faust/Info.plist
    XCODE_ATTRIBUTE_FRAMEWORK_SEARCH_PATHS "/System/Library/PrivateFrameworks /Library/Frameworks"
)

# Basic includes
include_directories(${PROJECT_SOURCE_DIR}/thirdparty/faust/architecture)
include_directories(${PROJECT_SOURCE_DIR}/thirdparty/faust/compiler)
include_directories(${PROJECT_SOURCE_DIR}/thirdparty/faust/compiler/utils)
include_directories(${TOUCHDESIGNER_INC})

# Link libfaust based on platform
target_link_directories(${PROJECT_NAME} PRIVATE ${LIBFAUST_DIR}/lib)
if(MSVC)
target_link_libraries(${PROJECT_NAME} PRIVATE libfaustwithllvm.lib)
else()
target_link_libraries(${PROJECT_NAME} PRIVATE libfaustwithllvm.a)
endif()

# Find sndfile and link it
if (MSVC)
    find_package(SndFile REQUIRED HINTS "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/libsndfile-1.2.0-win64/cmake")
    target_link_libraries(${PROJECT_NAME} PRIVATE SndFile::sndfile)
else()
    find_package(PkgConfig REQUIRED)
    # We expect the user to have used brew to install the dependencies
    # for libsndfile, to have built libsndfile as a static lib,
    # and for it to be accessible via `pkg-config --static libsndfile`.
    set(CMAKE_FIND_LIBRARY_SUFFIXES .a)
    list(APPEND PKG_CONFIG_EXECUTABLE "--static")  # append temporarily
    pkg_check_modules(SNDFILE REQUIRED IMPORTED_TARGET sndfile)
    pkg_check_modules(FLAC REQUIRED IMPORTED_TARGET flac)
    pkg_check_modules(VORBIS REQUIRED IMPORTED_TARGET vorbis)
    pkg_check_modules(OGG REQUIRED IMPORTED_TARGET ogg)
    pkg_check_modules(OPUS REQUIRED IMPORTED_TARGET opus)
    pkg_check_modules(MPG123 REQUIRED IMPORTED_TARGET libmpg123)
    list(POP_BACK PKG_CONFIG_EXECUTABLE)  # undo the append above
    target_link_libraries (${PROJECT_NAME} PRIVATE PkgConfig::SNDFILE PkgConfig::FLAC PkgConfig::VORBIS PkgConfig::OGG PkgConfig::OPUS PkgConfig::MPG123)
endif()

# Link against Python
set(Python_FIND_REGISTRY "LAST")
set(Python_FIND_STRATEGY "LOCATION")
find_package(Python ${PYTHONVER} EXACT REQUIRED COMPONENTS Interpreter Development)
target_link_libraries(${PROJECT_NAME} PRIVATE Python::Python)

# Platform-specific libraries and definitions
if(APPLE)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "__APPLE__")
    target_link_libraries(${PROJECT_NAME} PRIVATE "-framework CoreFoundation" "-framework CoreMIDI" "-framework CoreAudio")
elseif(MSVC)
    # win sock 32; windows multimedia for rt midi
    target_link_libraries(${PROJECT_NAME} PRIVATE winmm ws2_32)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "WIN32;_WIN32;_WINDOWS;__WINDOWS_DS__;")
endif()

if(MSVC)
    set_target_properties(${PROJECT_NAME} PROPERTIES
                          VS_DEBUGGER_COMMAND "C:\\Program Files\\Derivative\\TouchDesigner\\bin\\TouchDesigner.exe"
                          VS_DEBUGGER_COMMAND_ARGUMENTS "..\\$(ProjectName).toe")
endif()

if(APPLE)
    # Make two attempts to fix the python location because different users will have Python installed
    # in different locations. We need the python location to point to TouchDesigner's version.
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD COMMAND
        install_name_tool -change /Library/Frameworks/Python.framework/Versions/${PYTHONVER}/Python $TOUCHDESIGNER_APP/Contents/Frameworks/Python.framework/Versions/${PYTHONVER}/lib/libpython${PYTHONVER}.dylib "$<TARGET_FILE:TD-Faust>"
        )
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD COMMAND
        install_name_tool -change @rpath/Python3.framework/Versions/${PYTHONVER}/Python3 $TOUCHDESIGNER_APP/Contents/Frameworks/Python.framework/Versions/${PYTHONVER}/lib/libpython${PYTHONVER}.dylib "$<TARGET_FILE:TD-Faust>"
        )
else()
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD COMMAND
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_FILE:TD-Faust>" ${CMAKE_SOURCE_DIR}/Plugins
        )
endif()
