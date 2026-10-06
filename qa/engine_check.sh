#!/bin/bash
# Replays the bundled GPS tracks through the Swift SkiEngine and checks the totals match the web app's.
# Expected numbers come from replaying the same tracks through the web page (qa: js_replay).
set -e
OUT="${1:-qa-out/engine}"; mkdir -p "$OUT"
swiftc -O ios/Shared/SkiEngine.swift ios/Shared/Replay/main.swift -o "$OUT/replay"
D=ios/Shared/TestData; G=ios/SkiNav/Simulate
check () { # name gpx lifts steps expected_km
  r=$("$OUT/replay" "$2" "$3" $4)
  ok=$(python3 -c "import json,sys; r=json.loads('$r'); print('true' if abs(r['km']-$5)<=0.05 else 'false')")
  echo "[web] QA RESULT {\"check\":\"native engine matches web: $1\",\"ok\":$ok,\"detail\":\"swift $(echo $r | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["km"],"km, max",r["maxKmh"],"km/h, vert",r["vertM"],"m")') vs web $5 km\"}" | tee -a "$OUT/log.txt"
}
check "Avoriaz day 1" $G/Avoriaz-Day1.gpx $D/avoriaz-lifts.json $D/avoriaz-day1-steps.json 33.49
check "NYC practice" $G/NYC-Practice.gpx $D/nyc-lifts.json $D/nyc-steps.json 8.05
echo "[web] QA DONE" >> "$OUT/log.txt"
