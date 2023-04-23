cmake_minimum_required(VERSION 3.13.0 FATAL_ERROR)

set(VERSION 0.2.0)
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

# Link TD-Faust against faustlib
include_directories(${PROJECT_SOURCE_DIR}/thirdparty/libfaust/include)
if(APPLE)
target_link_libraries(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/thirdparty/libfaust/lib/libfaustwithllvm.a)
elseif(MSVC)
target_link_libraries(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/thirdparty/libfaust/lib/libfaustwithllvm.lib)
endif()

# Link against sndfile
find_package(SndFile REQUIRED)
target_link_libraries(${PROJECT_NAME} SndFile::sndfile)

# Link against Python
set(Python_FIND_REGISTRY "LAST")
set(Python_FIND_STRATEGY "LOCATION")
find_package(Python ${PYTHONVER} EXACT REQUIRED COMPONENTS Interpreter Development)
target_link_libraries(${PROJECT_NAME} Python::Python)

# Platform-specific libraries and definitions
if(APPLE)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "__APPLE__")
    target_link_libraries(${PROJECT_NAME} "-framework CoreFoundation" "-framework CoreMIDI" "-framework CoreAudio")
elseif(MSVC)
    # win sock 32; windows multimedia for rt midi
    target_link_libraries(${PROJECT_NAME} winmmm ws2_32)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "WIN32;_WIN32;_WINDOWS;__WINDOWS_DS__;")
endif()

if(MSVC)
    set_target_properties(${PROJECT_NAME} PROPERTIES
                          VS_DEBUGGER_COMMAND "C:\\Program Files\\Derivative\\TouchDesigner\\bin\\TouchDesigner.exe"
                          VS_DEBUGGER_COMMAND_ARGUMENTS "..\\$(ProjectName).toe")
endif()

if(APPLE)
    add_custom_command(TARGET ${PROJECT_NAME} 
                     POST_BUILD
                     COMMAND install_name_tool -change /Library/Frameworks/Python.framework/Versions/${PYTHONVER}/Python $TOUCHDESIGNER_APP/Contents/Frameworks/Python.framework/Versions/${PYTHONVER}/lib/libpython${PYTHONVER}.dylib "$<TARGET_FILE:TD-Faust>"
                     )
else()
    add_custom_command(TARGET ${PROJECT_NAME}
                       POST_BUILD
                       COMMAND ${CMAKE_COMMAND} -E copy_if_different
                       "$<TARGET_FILE:TD-Faust>"
                       ${CMAKE_SOURCE_DIR}/Plugins
                       )
endif()
