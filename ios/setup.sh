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
if [ "${1:-}" = "--no-watch" ]; then
  # phone only: same project, but the iPhone app doesn't embed (or need to sign) the Watch app
  sed '/^    dependencies:/,/target: SkiNavWatch/d' project.yml > .project-phone.yml
  xcodegen generate --spec .project-phone.yml --project .
  rm .project-phone.yml
  echo "Phone-only project (no Watch app). Run ./setup.sh without --no-watch to bring the Watch back."
else
  xcodegen generate
fi
open SkiNav.xcodeproj 2>/dev/null || true
