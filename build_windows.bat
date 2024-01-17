@echo off
setlocal enabledelayedexpansion

rem Remove any old plugins
rem rm Plugins/sndfile.dll
rem rm Plugins/TD-Faust.dll
rm build/CMakeCache.txt

if "%PYTHONVER%"=="" (
    set PYTHONVER=3.11
)
echo "Using Python version: %PYTHONVER%"

rem Download libsndfile
if not exist "thirdparty/libsndfile-1.2.0-win64/" (
    echo "Downloading libsndfile..." 
    cd thirdparty
    curl -OL https://github.com/libsndfile/libsndfile/releases/download/1.2.0/libsndfile-1.2.0-win64.zip
    7z x libsndfile-1.2.0-win64.zip -y
    rm libsndfile-1.2.0-win64.zip
    echo "Downloaded libsndfile." 
    cd ..
)

rem Use CMake for TD-Faust
cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DLIBFAUST_DIR="thirdparty/libfaust/win64/Release" -DSndFile_DIR=thirdparty/libsndfile/build -DPYTHONVER=%PYTHONVER%

rem Build TD-Faust
cmake --build build --config Release

cp "thirdparty/libsndfile-1.2.0-win64/bin/sndfile.dll" "Plugins/sndfile.dll"

echo "All Done!"