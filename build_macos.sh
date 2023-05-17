# Remove any old plugins and dylib
rm -r Plugins/TD-Faust.plugin

if [ "$TOUCHDESIGNER_APP" == "" ]; then
    # a reasonable default in case you forget to set the path to TouchDesigner.
    export TOUCHDESIGNER_APP=/Applications/TouchDesigner.app
fi

if [ "$PYTHONVER" == "" ]; then
    # Guess which Python version TD uses.
    export PYTHONVER=3.9
fi

export CMAKE_OSX_DEPLOYMENT_TARGET=11.0

if [[ $(uname -m) == 'arm64' ]]; then
    export LIBFAUST_DIR=$PWD/thirdparty/libfaust/darwin-arm64/Release
else
    export LIBFAUST_DIR=$PWD/thirdparty/libfaust/darwin-x64/Release
fi

# Build libsndfile
echo "Building libsndfile."
cd thirdparty/libsndfile
cmake -Bbuild $CMAKEOPTS -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_INSTALL_PREFIX="./install"
cmake --build build --config Release
cmake --build build --target install
cd ../..

# Use CMake for TD-Faust
cmake -Bbuild -G "Xcode" -DCMAKE_OSX_DEPLOYMENT_TARGET=$CMAKE_OSX_DEPLOYMENT_TARGET -DLIBFAUST_DIR="$LIBFAUST_DIR" -DSndFile_DIR="thirdparty/libsndfile/install" -DPYTHONVER=$PYTHONVER

# Build TD-Faust (Release)
xcodebuild -configuration Release -project build/TD-Faust.xcodeproj

# # Copy to Plugins directory
mv build/Release/TD-Faust.plugin Plugins

echo "All Done!"