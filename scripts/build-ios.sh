#!/bin/bash
npm run build
npx cap sync ios
# Requires macOS and Xcode
echo "Open ios/App/App.xcworkspace in Xcode to build the IPA."
