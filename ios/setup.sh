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
# signing team: Alon's paid team is in project.yml. To build with another team once: ./setup.sh --team ABCDE12345
# (remembered in .team-override; delete that file to go back to the default)
[ -n "$TEAM_ARG" ] && echo "$TEAM_ARG" > .team-override
if [ -s .team-override ]; then
  TEAM=$(tr -d ' \n' < .team-override)
  sed -E "s/DEVELOPMENT_TEAM: \"[A-Z0-9]*\"/DEVELOPMENT_TEAM: \"$TEAM\"/" .project-gen.yml > .project-tmp.yml && mv .project-tmp.yml .project-gen.yml
fi
echo "Signing team: $(sed -n 's/.*DEVELOPMENT_TEAM: \"\([A-Z0-9]*\)\".*/\1/p' .project-gen.yml | head -1)"
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
