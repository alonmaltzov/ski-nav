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
# a paired Apple Watch simulator, to test phone -> watch sync (plan + live stats).
# Prefer a phone/watch pair the machine already has; otherwise create and pair a watch.
WATCH=""
PAIR=$(xcrun simctl list pairs -j | python3 -c "
import json,sys
p=json.load(sys.stdin).get('pairs',{})
ok=[(v['phone']['udid'],k,v['watch']['udid'],v['phone'].get('name','')) for k,v in p.items() if 'iPhone' in v['phone'].get('name','')]
pref=[x for x in ok if '16' in x[3]] or ok
print(' '.join(pref[0][:3]) if pref else '')")
echo "[runner] existing pairs pick: ${PAIR:-none}" >> "$OUT/runner.txt"
if [ -n "$PAIR" ]; then
  UDID=$(echo $PAIR | cut -d' ' -f1); PAIRID=$(echo $PAIR | cut -d' ' -f2); WATCH=$(echo $PAIR | cut -d' ' -f3)
  xcrun simctl pair_activate "$PAIRID" >>"$OUT/runner.txt" 2>&1 || true
  NAME=$(xcrun simctl list devices | grep "$UDID" | sed 's/ (.*//' | xargs); echo "$NAME" > "$OUT/device.txt"
  echo "Using existing pair: phone $UDID ($NAME), watch $WATCH"
else
  # newest watchOS runtime, a watch model that runtime supports, and an iPhone on the matching iOS (26 <-> 26, 18 <-> 11)
  read WRT WDT PHONE_RT <<< "$(xcrun simctl list runtimes -j | python3 -c "
import json,sys
rs=[x for x in json.load(sys.stdin)['runtimes'] if x.get('isAvailable')]
w=[x for x in rs if x['platform']=='watchOS']
if not w: print('- - -'); sys.exit()
w=w[-1]; wm=int(w['version'].split('.')[0])
types=[d for d in w.get('supportedDeviceTypes',[]) if d['name'].startswith('Apple Watch Series') or d['name'].startswith('Apple Watch Ultra')]
im = wm if wm>=26 else wm+7
ios=[x for x in rs if x['platform']=='iOS' and int(x['version'].split('.')[0])==im] or [x for x in rs if x['platform']=='iOS']
print(w['identifier'], types[-1]['identifier'] if types else '-', ios[-1]['identifier'])")"
  if [ "$PHONE_RT" != "-" ]; then
    P2=$(xcrun simctl list devices available -j | python3 -c "
import json,sys
d=json.load(sys.stdin)['devices'].get('$PHONE_RT',[])
c=[x for x in d if x['name'].startswith('iPhone')]
pref=[x for x in c if 'Pro' in x['name'] and 'Max' not in x['name']] or c
print(pref[0]['udid'] if pref else '')")
    if [ -n "$P2" ]; then UDID=$P2; NAME=$(xcrun simctl list devices | grep "$UDID" | sed 's/ (.*//' | xargs); echo "$NAME" > "$OUT/device.txt"; fi
  fi
  [ "$WRT" = "-" ] && WRT=""; [ "$WDT" = "-" ] && WDT=""
  echo "[runner] watch runtime=$WRT type=$WDT" >> "$OUT/runner.txt"
  if [ -n "$WRT" ] && [ -n "$WDT" ]; then
    xcrun simctl shutdown "$UDID" >/dev/null 2>&1 || true
    WATCH=$(xcrun simctl create "QA Watch" "$WDT" "$WRT" 2>>"$OUT/runner.txt" || true)
    if [ -z "$WATCH" ] || ! xcrun simctl pair "$WATCH" "$UDID" >>"$OUT/runner.txt" 2>&1; then echo "[app] watch pairing failed" >> "$OUT/runner.txt"; WATCH=""; fi
  fi
fi
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b
xcrun simctl install "$UDID" "$APP"
if [ -n "$WATCH" ]; then
  xcrun simctl boot "$WATCH" 2>/dev/null || true
  xcrun simctl bootstatus "$WATCH" -b
  WAPP=$(ls -d "$APP"/Watch/*.app | head -1)
  WBUNDLE=$(/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" "$WAPP/Info.plist")
  xcrun simctl install "$WATCH" "$WAPP" && echo "Watch app installed: $WBUNDLE"
  xcrun simctl launch --console-pty "$WATCH" "$WBUNDLE" > "$OUT/watch.log" 2>&1 &
  WPID=$!
  sleep 8
fi
xcrun simctl privacy "$UDID" grant location-always "$BUNDLE" || xcrun simctl privacy "$UDID" grant location "$BUNDLE" || true
xcrun simctl location "$UDID" set 46.193310,6.768150 || true

# app prints [app] / [web] lines; the tour logs QA SCREEN / AUDIT / RESULT / DONE
xcrun simctl launch --console-pty --terminate-running-process "$UDID" "$BUNDLE" -qaTour > "$OUT/log.txt" 2>&1 &
LPID=$!
seen=0; start=$(date +%s); moving=0
while true; do
  # skier moving down the first runs at ~36 km/h, started when the tour reaches its GPS part
  if [ $moving = 0 ] && grep -q "QA GPS START" "$OUT/log.txt"; then
    moving=1
    # headless simulators ignore 'simctl location start', so step the location ourselves: 10 m every second
    ( for p in $(python3 qa/sim_waypoints.py 10); do xcrun simctl location "$UDID" set "$p" >/dev/null 2>&1; sleep 0.5; done ) &
    MOVER=$!
    echo "[runner] moving route started" >> "$OUT/runner.txt"
  fi
  n=$(grep -c "QA SCREEN" "$OUT/log.txt" 2>/dev/null || echo 0)
  while [ "$seen" -lt "$n" ]; do
    seen=$((seen+1))
    s=$(grep "QA SCREEN" "$OUT/log.txt" | sed -n "${seen}p" | sed 's/.*QA SCREEN //' | tr -cd 'a-zA-Z0-9_-')
    sleep 0.8
    xcrun simctl io "$UDID" screenshot "$OUT/$(printf %02d $seen)-$s.png" >/dev/null 2>&1 || true
    if [ -n "$WATCH" ] && [ "$s" = "gps-tracking" ]; then xcrun simctl io "$WATCH" screenshot "$OUT/$(printf %02d $seen)-watch-live.png" >/dev/null 2>&1 || true; fi
  done
  grep -q "QA DONE" "$OUT/log.txt" && break
  [ $(( $(date +%s) - start )) -gt 480 ] && { echo '[web] QA RESULT {"check":"tour finished in time","ok":false,"detail":"timeout after 8 min"}' >> "$OUT/log.txt"; break; }
  sleep 0.3
done
kill ${MOVER:-0} 2>/dev/null; xcrun simctl location "$UDID" clear || true
xcrun simctl io "$UDID" screenshot "$OUT/99-final.png" >/dev/null 2>&1 || true
kill $LPID 2>/dev/null || true
if [ -n "$WATCH" ]; then
  xcrun simctl io "$WATCH" screenshot "$OUT/98-watch.png" >/dev/null 2>&1 || true
  kill ${WPID:-0} 2>/dev/null || true
  plan=$(grep -m1 "\[watch\] plan received" "$OUT/watch.log" | sed 's/.*plan received: //' | tr -d '\r"')
  live=$(grep -m1 "\[watch\] live data" "$OUT/watch.log" | sed 's/.*from phone: //' | tr -d '\r"')
  phonelink=$(grep -m1 "\[app\] watch link" "$OUT/log.txt" | tr -d '\r"')
  [ -n "$plan" ] && ok=true || ok=false
  echo "[web] QA RESULT {\"check\":\"watch receives today's plan from the phone\",\"ok\":$ok,\"detail\":\"${plan:-nothing received} | ${phonelink}\"}" >> "$OUT/log.txt"
  [ -n "$live" ] && ok=true || ok=false
  echo "[web] QA RESULT {\"check\":\"watch shows live stats while the phone tracks\",\"ok\":$ok,\"detail\":\"${live:-no live data}\"}" >> "$OUT/log.txt"
fi
echo "QA screens captured: $seen"
