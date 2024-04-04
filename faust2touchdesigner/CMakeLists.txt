cmake_minimum_required(VERSION 3.13.0 FATAL_ERROR)

set(VERSION 0.0.1)
project(${OP_TYPE} VERSION ${VERSION})

set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT ${OP_TYPE})

set(TOUCHDESIGNER_INC ${PROJECT_SOURCE_DIR}/../thirdparty/TouchDesigner/)

set(Headers
    "${TOUCHDESIGNER_INC}/CHOP_CPlusPlusBase.h"
    "${TOUCHDESIGNER_INC}/CPlusPlus_Common.h"
    "${TOUCHDESIGNER_INC}/GL_Extensions.h"
    "${PROJECT_SOURCE_DIR}/Faust_${OP_TYPE}_CHOP.h"
    "${PROJECT_SOURCE_DIR}/${OP_TYPE}.h"
)
source_group("Headers" FILES ${Headers})

set(Sources
    "${PROJECT_SOURCE_DIR}/Faust_${OP_TYPE}_CHOP.cpp"
)

source_group("Sources" FILES ${Sources})

set(ALL_FILES
    ${Headers}
    ${Sources}
)

add_library(${OP_TYPE} MODULE ${ALL_FILES})

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
    MACOSX_BUNDLE_COPYRIGHT "${AUTHOR_NAME}"
    MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_SOURCE_DIR}/Info.plist
    XCODE_ATTRIBUTE_FRAMEWORK_SEARCH_PATHS "/System/Library/PrivateFrameworks /Library/Frameworks"
)

include_directories(${LIBFAUST_DIR}/include)
include_directories(${LIBFAUST_DIR}/include/faust/architecture)
include_directories(${LIBFAUST_DIR}/include/faust/compiler)
include_directories(${LIBFAUST_DIR}/include/faust/compiler/utils)
include_directories(${TOUCHDESIGNER_INC})

target_compile_definitions(${PROJECT_NAME} PRIVATE "OP_TYPE=${OP_TYPE}")

# Platform-specific libraries and definitions
if(APPLE)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "__APPLE__")
    # target_link_libraries(${PROJECT_NAME} PRIVATE "-framework CoreFoundation" "-framework CoreMIDI" "-framework CoreAudio")
elseif(MSVC)
    # win sock 32; windows multimedia for rt midi
    # target_link_libraries(${PROJECT_NAME} PRIVATE winmm ws2_32)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "WIN32;_WIN32;_WINDOWS;__WINDOWS_DS__;")
endif()

if(MSVC)
    set_target_properties(${PROJECT_NAME} PROPERTIES
                          VS_DEBUGGER_COMMAND "C:\\Program Files\\Derivative\\TouchDesigner\\bin\\TouchDesigner.exe"
                          VS_DEBUGGER_COMMAND_ARGUMENTS "..\\$(ProjectName).toe")

    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD COMMAND
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_FILE:${PROJECT_NAME}>" ${CMAKE_SOURCE_DIR}/../Plugins
        )
endif()
