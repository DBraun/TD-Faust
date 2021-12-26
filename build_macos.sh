# Remove any old plugins and dylib
rm Plugins/libfaust.2.dylib
rm -r Plugins/TD-Faust.plugin

# Download LLVM
if [ ! -d "thirdparty/clang+llvm-12.0.0-x86_64-apple-darwin/" ] 
then
    echo "Directory thirdparty/clang+llvm-12.0.0-x86_64-apple-darwin DOES NOT exist." 
	cd thirdparty
	curl -OL https://github.com/llvm/llvm-project/releases/download/llvmorg-12.0.0/clang+llvm-12.0.0-x86_64-apple-darwin.tar.xz
	tar -xf clang+llvm-12.0.0-x86_64-apple-darwin.tar.xz
	# rm clang+llvm-12.0.0-x86_64-apple-darwin.tar.xz
	cd ..
fi

# Build libsndfile
# brew install autoconf autogen automake flac libogg libtool libvorbis opus mpg123 pkg-config speex
mkdir thirdparty/libsndfile/build
cd thirdparty/libsndfile/build
# todo: enable external libs and do the brew install of those codecs.
# The reason we can't do this yet is that we're building/using everything x86_64 instead of macos-arm64
cmake .. -G "Unix Makefiles" -DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE=ON -DENABLE_EXTERNAL_LIBS=off
cmake --build . --config Release
cd ../../..

# Use CMake for TD-Faust
cmake -Bbuild -DUSE_LLVM_CONFIG=off -G "Xcode" -DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_PREFIX_PATH=$PWD/thirdparty/clang+llvm-12.0.0-x86_64-apple-darwin/lib/cmake/llvm -DSndFile_DIR=thirdparty/libsndfile/build
cmake -Bbuild -DUSE_LLVM_CONFIG=off -G "Xcode" -DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_PREFIX_PATH=$PWD/thirdparty/clang+llvm-12.0.0-x86_64-apple-darwin/lib/cmake/llvm -DSndFile_DIR=thirdparty/libsndfile/build

# Build TD-Faust (Release)
xcodebuild -configuration Release -project build/TD-Faust.xcodeproj/
mv thirdparty/faust/build/lib/Release/libfaust.2.38.7.dylib thirdparty/faust/build/lib/Release/libfaust.2.dylib

# Steps so that libfaust.2.dylib is found as a dependency
install_name_tool -change @rpath/libfaust.2.dylib @loader_path/../../../libfaust.2.dylib Release/TD-Faust.plugin/Contents/MacOS/TD-Faust

# codesigning
# Open Keychain Access. Go to "login". Look for "Apple Development".
# run `export CODESIGN_IDENTITY="Apple Development: example@example.com (ABCDE12345)"` with your own info substituted.
codesign --force --deep --sign "$CODESIGN_IDENTITY" Release/TD-Faust.plugin/Contents/MacOS/TD-Faust

# # Confirm the codesigning
codesign -vvvv Release/TD-Faust.plugin/Contents/MacOS/TD-Faust

# # Copy to Plugins directory
mv thirdparty/faust/build/lib/Release/libfaust.2.dylib Plugins
mv Release/TD-Faust.plugin Plugins

echo "All Done!"