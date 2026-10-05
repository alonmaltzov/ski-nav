"""Print ~60 'lat,lon' waypoints covering the first ~3 km of the Avoriaz Day 1 GPX (for simctl location start)."""
import re, math, sys, os
gpx = open(os.path.join(os.path.dirname(__file__), '..', 'ios', 'SkiNav', 'Simulate', 'Avoriaz-Day1.gpx')).read()
pts = [(float(a), float(b)) for a, b in re.findall(r'lat="([-\d.]+)"\s+lon="([-\d.]+)"', gpx)]
out, dist, last = [pts[0]], 0.0, pts[0]
for p in pts[1:]:
    d = math.hypot((p[0] - last[0]) * 111320, (p[1] - last[1]) * 111320 * math.cos(math.radians(p[0])))
    if d >= 40: out.append(p); dist += d; last = p
    if dist > 3000: break
print(' '.join(f'{a:.6f},{b:.6f}' for a, b in out))
