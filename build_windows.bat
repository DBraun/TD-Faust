rem Remove any old plugins
rem rm Plugins/faust.dll
rem rm Plugins/TD-Faust.dll
rm build/CMakeCache.txt

rem Faust-2.58.18-win64.exe /S /D=%cd%\libfaust\windows-x86_64

rem Build libsndfile
if not exist "thirdparty/libsndfile/build" (
    echo "Building Libsndfile."
    cd thirdparty/libsndfile
    cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE=ON -DBUILD_SHARED_LIBS=ON
    cmake --build build --config Release
    cp build/Release/sndfile.dll ../../Plugins/sndfile.dll
    cd ../..
)

rem Use CMake for TD-Faust
cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DSndFile_DIR=thirdparty/libsndfile/build -DPYTHONVER="3.9"

rem Build TD-Faust
cmake --build build --config Release

echo "All Done!"