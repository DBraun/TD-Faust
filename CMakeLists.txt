cmake_minimum_required(VERSION 3.13.0 FATAL_ERROR)

project(TD-Faust VERSION 0.0.1)

set(LLVM_DIR ${LLVM_DIR})
set(SndFile_DIR ${SndFile_DIR})
# set(SNDFILE_INCLUDE_DIR ${SndFile_DIR}/include)

include(FaustLib.cmake)
## Create Faust
message(STATUS "TD-Faust external")

set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT TD-Faust)

################################################################################
# Set target arch type if empty. Visual studio solution generator provides it.
################################################################################
if(NOT CMAKE_VS_PLATFORM_NAME)
    set(CMAKE_VS_PLATFORM_NAME "x64")
endif()
message("${CMAKE_VS_PLATFORM_NAME} architecture in use")

if(NOT ("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64"))
    message(FATAL_ERROR "${CMAKE_VS_PLATFORM_NAME} arch is not supported!")
endif()

################################################################################
# Common utils
################################################################################
include(CMake/Utils.cmake)

################################################################################
# Additional Global Settings(add specific info there)
################################################################################
include(CMake/GlobalSettingsInclude.cmake OPTIONAL)

################################################################################
# Use solution folders feature
################################################################################
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

################################################################################
# Sub-projects
################################################################################

project(TD-Faust VERSION 0.0.1)

if(APPLE OR MSVC)

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
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_EXTENSIONS OFF
    BUNDLE true
    BUNDLE_EXTENSION "plugin"
    MACOSX_BUNDLE_GUI_IDENTIFIER design.dirt.cpp.${PROJECT_NAME}
    MACOSX_BUNDLE_INFO_STRING ${PROJECT_NAME}
    MACOSX_BUNDLE_BUNDLE_NAME ${PROJECT_NAME}
    MACOSX_BUNDLE_BUNDLE_VERSION "0.1"
    MACOSX_BUNDLE_SHORT_VERSION_STRING "0.1"
    MACOSX_BUNDLE_COPYRIGHT "David Braun"
    # MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_SOURCE_DIR}/src/Info.plist
    )

if (!WIN32) 
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -stdlib=libc++")
endif()

## Link TD-Faust with faustlib
include_directories(${PROJECT_SOURCE_DIR}/thirdparty/faust/architecture)
include_directories(${PROJECT_SOURCE_DIR}/thirdparty/faust/compiler)
include_directories(${PROJECT_SOURCE_DIR}/thirdparty/faust/compiler/utils)
include_directories(${TOUCHDESIGNER_INC})
add_dependencies(${PROJECT_NAME} dynamiclib)
target_link_libraries(${PROJECT_NAME} dynamiclib)

include (CMakeFindDependencyMacro)

find_package(SndFile REQUIRED)
target_link_libraries(${PROJECT_NAME} SndFile::sndfile)

## Link the Pure Data external with llvm
find_package(LLVM REQUIRED CONFIG)
message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})

if(WIN32)
  # win sock 32
  target_link_libraries(${PROJECT_NAME} ws2_32)
  # windows multimedia for rt midi
  target_link_libraries(${PROJECT_NAME} winmm)
elseif(APPLE)
  target_link_libraries(${PROJECT_NAME} "-framework CoreFoundation" "-framework CoreMIDI" "-framework CoreAudio")
endif()

else()
## pretend we're building on Linux
add_library(TD-Faust MODULE "${PROJECT_SOURCE_DIR}/TD-Faust/null.cpp")
add_dependencies(${PROJECT_NAME} dynamiclib)
target_link_libraries(${PROJECT_NAME} dynamiclib)

endif()

if(MSVC)
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS " /ignore:4099 ")
endif()

use_props(${PROJECT_NAME} "${CMAKE_CONFIGURATION_TYPES}" "${DEFAULT_CXX_PROPS}")
set(ROOT_NAMESPACE ${PROJECT_NAME})


################################################################################
# Output directory
################################################################################
set_target_properties(${PROJECT_NAME} PROPERTIES
    OUTPUT_DIRECTORY_DEBUG   "${CMAKE_SOURCE_DIR}/$<CONFIG>/"
    OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/$<CONFIG>/"
)
set_target_properties(${PROJECT_NAME} PROPERTIES
    INTERPROCEDURAL_OPTIMIZATION_RELEASE "TRUE"
)
################################################################################
# Compile definitions
################################################################################
target_compile_definitions(${PROJECT_NAME} PRIVATE
    "$<$<CONFIG:Debug>:"
        "_DEBUG"
    ">"
    "$<$<CONFIG:Release>:"
        "NDEBUG"
    ">"
    "_USRDLL;"
    "FAUSTCHOP_EXPORTS"
)

if(MSVC)

    set_target_properties(${PROJECT_NAME} PROPERTIES
        VS_GLOBAL_KEYWORD "Win32Proj"
    )

    target_compile_definitions(${PROJECT_NAME} PRIVATE
        "WIN32;"
        "_WIN32;"
        "_WINDOWS;"
        "__WINDOWS_DS__"
    )

endif()

################################################################################
# Compile and link options
################################################################################
if(MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE
        $<$<CONFIG:Debug>:
            /Od;
            /RTC1;
            /MDd
        >
        $<$<CONFIG:Release>:
            /MD
        >
        /W3;
        /Zi;
        ${DEFAULT_CXX_EXCEPTION_HANDLING};
        /Y-
    )
    target_link_options(${PROJECT_NAME} PRIVATE
        $<$<CONFIG:Release>:
            /OPT:REF;
            /OPT:ICF
        >
        /DEBUG;
        /SUBSYSTEM:WINDOWS;
        /INCREMENTAL:NO
    )
endif()

if(MSVC)
    set_target_properties(${PROJECT_NAME} PROPERTIES
                          VS_DEBUGGER_COMMAND "C:\\Program Files\\Derivative\\TouchDesigner\\bin\\TouchDesigner.exe"
                          VS_DEBUGGER_COMMAND_ARGUMENTS "..\\$(ProjectName).toe")
endif()

# The following step will create a post-build event that copies the custom DLL to
# the Plugins folder.
if(APPLE)
## For some reason if you move the file like this, it fails to load in TD.
#  add_custom_command(TARGET ${PROJECT_NAME}
#                     POST_BUILD
#                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
#                     "$<TARGET_FILE:TD-Faust>"
#                     ${CMAKE_SOURCE_DIR}/Plugins/${PROJECT_NAME}.plugin)
else()
  add_custom_command(TARGET ${PROJECT_NAME}
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     "$<TARGET_FILE:TD-Faust>"
                     ${CMAKE_SOURCE_DIR}/Plugins)
endif()
  add_custom_command(TARGET ${PROJECT_NAME}
                     POST_BUILD
                     COMMAND ${CMAKE_COMMAND} -E copy_if_different
                     "$<TARGET_FILE:dynamiclib>"
                     ${CMAKE_SOURCE_DIR}/Plugins)
