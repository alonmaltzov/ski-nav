#!/bin/bash
# Run on your Mac from the ios folder: ./setup.sh
set -e
cd "$(dirname "$0")"
command -v xcodegen >/dev/null || { echo "Installing XcodeGen (needs Homebrew)…"; brew install xcodegen; }
cp ../index.html SkiNav/www/index.html
xcodegen generate
open SkiNav.xcodeproj
