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
# options: --no-watch (phone only), --beta (installs as a separate "Ski Nav Beta" app next to the regular one)
NOWATCH=0; BETA=0
TEAM_ARG=""
while [ $# -gt 0 ]; do case "$1" in --no-watch) NOWATCH=1;; --beta) BETA=1;; --team) TEAM_ARG="$2"; shift;; esac; shift; done
cp project.yml .project-gen.yml
# signing team: remembered in .team so you don't pick it in Xcode after every update
# (--team ABCDE12345 to change it; otherwise found from your Apple Development certificate)
[ -n "$TEAM_ARG" ] && echo "$TEAM_ARG" > .team
if [ ! -s .team ]; then
  T=$(security find-certificate -c "Apple Development" -p 2>/dev/null | openssl x509 -noout -subject 2>/dev/null | sed -n 's/.*OU *= *\([A-Z0-9]\{10\}\).*/\1/p' | head -1)
  [ -n "$T" ] && echo "$T" > .team
fi
if [ -s .team ]; then
  TEAM=$(tr -d ' \n' < .team)
  sed "s/DEVELOPMENT_TEAM: \"\"/DEVELOPMENT_TEAM: \"$TEAM\"/" .project-gen.yml > .project-tmp.yml && mv .project-tmp.yml .project-gen.yml
  echo "Signing team: $TEAM"
else
  echo "No signing team found: pick your team once in Xcode > Signing & Capabilities."
fi
if [ $NOWATCH = 1 ]; then
  awk '/^  SkiNavWatch:/{skip=1} /^  SkiNavWidgets:/{skip=0} /^schemes:/{skip=0} /- target: SkiNavWatch/{next} /SkiNavWatch: all/{next} /SkiNavWatchWidgets: all/{next} !skip' .project-gen.yml > .project-tmp.yml && mv .project-tmp.yml .project-gen.yml
  echo "Phone only (no Watch app)."
fi
if [ $BETA = 1 ]; then
  sed -e 's/com\.alonmaltzov\.SkiNav/com.alonmaltzov.SkiNavBeta/g' -e 's/CFBundleDisplayName: Ski Nav$/CFBundleDisplayName: Ski Nav Beta/' \
      -e 's/INFOPLIST_KEY_CFBundleDisplayName: Ski Nav$/INFOPLIST_KEY_CFBundleDisplayName: Ski Nav Beta/' .project-gen.yml > .project-tmp.yml && mv .project-tmp.yml .project-gen.yml
  echo "Beta build: installs as \"Ski Nav Beta\", separate from your regular Ski Nav."
fi
rm -rf SkiNav.xcodeproj
xcodegen generate --spec .project-gen.yml --project .
rm .project-gen.yml
open SkiNav.xcodeproj 2>/dev/null || true
