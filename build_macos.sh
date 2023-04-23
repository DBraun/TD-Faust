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

export CMAKE_OSX_DEPLOYMENT_TARGET=10.15

if [ -d "thirdparty/libsndfile/build" ] 
then
    echo "Skipping building of Libsndfile." 
else
    echo "Building Libsndfile."
    cd thirdparty/libsndfile
    cmake -Bbuild -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_OSX_DEPLOYMENT_TARGET=$CMAKE_OSX_DEPLOYMENT_TARGET
    cmake --build build --config Release
    cd ../..
fi

# Use CMake for TD-Faust
cmake -Bbuild -G "Xcode" -DCMAKE_OSX_DEPLOYMENT_TARGET=$CMAKE_OSX_DEPLOYMENT_TARGET -DSndFile_DIR=thirdparty/libsndfile/build -DPYTHONVER=$PYTHONVER

# Build TD-Faust (Release)
xcodebuild -configuration Release -project build/TD-Faust.xcodeproj

# # Copy to Plugins directory
mv build/Release/TD-Faust.plugin Plugins

echo "All Done!"