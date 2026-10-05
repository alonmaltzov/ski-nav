#!/bin/bash
# Runs the QA tour inside the real iPhone app in an iOS Simulator, with a moving simulated GPS.
# Usage (from repo root, after building): qa/sim_run.sh path/to/SkiNav.app [out-dir]
set -u
APP="$1"; OUT="${2:-qa-out/ios-sim}"; BUNDLE=com.alonmaltzov.SkiNav
mkdir -p "$OUT"
UDID=$(xcrun simctl list devices available -j | python3 -c "
import json,sys
d=json.load(sys.stdin)['devices']
c=[x for k,v in d.items() if 'iOS' in k for x in v if x['name'].startswith('iPhone')]
pref=[x for x in c if '16' in x['name'] and 'Plus' not in x['name'] and 'Max' not in x['name']] or c
print(pref[0]['udid'])")
NAME=$(xcrun simctl list devices | grep "$UDID" | sed 's/ (.*//' | xargs)
echo "Simulator: $NAME ($UDID)"; echo "$NAME" > "$OUT/device.txt"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b
xcrun simctl install "$UDID" "$APP"
xcrun simctl privacy "$UDID" grant location-always "$BUNDLE" || xcrun simctl privacy "$UDID" grant location "$BUNDLE" || true
xcrun simctl location "$UDID" set 46.193310,6.768150 || true

# app prints [app] / [web] lines; the tour logs QA SCREEN / AUDIT / RESULT / DONE
xcrun simctl launch --console-pty --terminate-running-process "$UDID" "$BUNDLE" -qaTour > "$OUT/log.txt" 2>&1 &
LPID=$!
# skier moving down the first runs at ~36 km/h, for the GPS part of the tour
sleep 20
xcrun simctl location "$UDID" start --speed=10 --interval=1 $(python3 qa/sim_waypoints.py) || echo "[app] simctl location start failed" >> "$OUT/log.txt"

seen=0; start=$(date +%s)
while true; do
  n=$(grep -c "QA SCREEN" "$OUT/log.txt" 2>/dev/null || echo 0)
  while [ "$seen" -lt "$n" ]; do
    seen=$((seen+1))
    s=$(grep "QA SCREEN" "$OUT/log.txt" | sed -n "${seen}p" | sed 's/.*QA SCREEN //' | tr -cd 'a-zA-Z0-9_-')
    sleep 0.8
    xcrun simctl io "$UDID" screenshot "$OUT/$(printf %02d $seen)-$s.png" >/dev/null 2>&1 || true
  done
  grep -q "QA DONE" "$OUT/log.txt" && break
  [ $(( $(date +%s) - start )) -gt 480 ] && { echo '[web] QA RESULT {"check":"tour finished in time","ok":false,"detail":"timeout after 8 min"}' >> "$OUT/log.txt"; break; }
  sleep 0.3
done
xcrun simctl location "$UDID" clear || true
xcrun simctl io "$UDID" screenshot "$OUT/99-final.png" >/dev/null 2>&1 || true
kill $LPID 2>/dev/null || true
echo "QA screens captured: $seen"
