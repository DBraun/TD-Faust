rem Remove any old plugins
rem rm Plugins/faust.dll
rem rm Plugins/TD-Faust.dll
rm build/CMakeCache.txt

rem Build LLVM
if not exist "thirdparty/llvm-project/llvm/build/" (
	echo "Building LLVM"
	cd thirdparty/llvm-project/llvm
	cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DLLVM_USE_CRT_DEBUG=MDd -DLLVM_USE_CRT_RELEASE=MD -DLLVM_BUILD_TESTS=Off -DCMAKE_INSTALL_PREFIX="./llvm" -Thost=x64 -DLLVM_ENABLE_ZLIB=off
	cmake --build build --config Release
	cd ../../../
)

rem Download libsndfile
if not exist "thirdparty/libsndfile-1.0.31-win64/" (
    echo "Downloading libsndfile..." 
	cd thirdparty
	curl -OL https://github.com/libsndfile/libsndfile/releases/download/1.0.31/libsndfile-1.0.31-win64.zip
	tar -xf libsndfile-1.0.31-win64.zip
	ls -r libsndfile-1.0.31-win64/*
	echo "Downloaded libsndfile." 
	cd ..
)

rem Use CMake for TD-Faust
set LLVM_DIR=%cd%/thirdparty/llvm-project/llvm/build/lib/cmake/llvm
echo "LLVM_DIR is " %LLVM_DIR%
cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DUSE_LLVM_CONFIG=off -DSndFile_DIR=thirdparty/libsndfile-1.0.31-win64/cmake

rem Build TD-Faust
cmake --build build --config Release

echo "All Done!"