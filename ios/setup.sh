#!/bin/bash
# Run on your Mac from the ios folder: ./setup.sh
set -e
cd "$(dirname "$0")"
command -v xcodegen >/dev/null || { echo "Installing XcodeGen (needs Homebrew)…"; brew install xcodegen; }
# the web app pages bundled inside the iPhone app (Avoriaz week, NYC practice, QA tour)
mkdir -p SkiNav/www
cp ../index.html SkiNav/www/index.html
cp ../nyc.html SkiNav/www/nyc.html
cp ../qa/tour.js SkiNav/www/qa-tour.js
xcodegen generate
open SkiNav.xcodeproj 2>/dev/null || true
