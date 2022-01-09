# Remove any old plugins and dylib
rm Plugins/libfaust.2.dylib
rm -r Plugins/TD-Faust.plugin

# # Build LLVM
# cd thirdparty/llvm-project/llvm
# cmake -Bbuild -DCMAKE_INSTALL_PREFIX="./llvm" -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" -DCMAKE_BUILD_TYPE=Release
# make --directory=build
# cd ../../..

# # Build libsndfile
# brew install autoconf autogen automake flac libogg libtool libvorbis opus mpg123 pkg-config speex
# mkdir thirdparty/libsndfile/build
# cd thirdparty/libsndfile/build
# # todo: enable external libs and do the brew install of those codecs.
# # The reason we can't do this yet is that we're building/using everything x86_64;arm64 instead of just one
# cmake .. -G "Unix Makefiles" -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE=ON -DENABLE_EXTERNAL_LIBS=off
# cmake --build . --config Release
# cd ../../..

# Use CMake for TD-Faust
cmake -Bbuild -DUSE_LLVM_CONFIG=off -G "Xcode" -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" -DCMAKE_PREFIX_PATH=$PWD/thirdparty/llvm-project/llvm/build/lib/cmake/llvm -DSndFile_DIR=thirdparty/libsndfile/build
cmake -Bbuild -DUSE_LLVM_CONFIG=off -G "Xcode" -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" -DCMAKE_PREFIX_PATH=$PWD/thirdparty/llvm-project/llvm/build/lib/cmake/llvm -DSndFile_DIR=thirdparty/libsndfile/build

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