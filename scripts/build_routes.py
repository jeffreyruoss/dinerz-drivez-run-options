#!/usr/bin/env python3
"""Fetch real walking geometry + distances for every leg via OSRM, emit routes.json."""
import json, time, urllib.request, urllib.parse

OSRM = "https://router.project-osrm.org/route/v1/foot/"

P = {  # geocoded (Nominatim) house-number-accurate coords
    "palmgrove":   (33.4950265, -111.9948832),
    "eatup":       (33.4948453, -111.9950300),
    "chopper":     (33.4948338, -112.0270040),
    "fivediner":   (33.5131897, -112.0476214),
    "totalwine":   (33.5103890, -112.0457482),
    "peakplaza":   (33.5373315, -112.0465225),
    "swizzle":     (33.5231432, -112.0469604),
    "luckyboy":    (33.4866224, -112.0477541),
    "desertsun":   (33.4573226, -112.0900848),
    "bikini":      (33.4590942, -112.0914383),
    "welcome":     (33.4556306, -112.0607910),
    "macalpines":  (33.4733407, -112.0647953),
    "azcenter":    (33.4524961, -112.0689749),
    "bethanytowne":(33.5259496, -112.1304323),
    "sonicbethany":(33.5244869, -112.1304149),
    "dennysbethany":(33.5243495,-112.1338353),
    "skippers":    (33.5258247, -112.1517154),
    "bethanysq":   (33.5240564, -112.1517279),
    "milltowne":   (33.3775471, -111.9369639),
    "monkeypants": (33.3935070, -111.9385507),
    "sonictempe":  (33.4083811, -111.9212024),
    "sunnys":      (33.4216931, -111.9087213),
    "tempemkt":    (33.4320733, -111.9040915),
    "hamburgerworks":(33.4800340,-112.0910970),
    "joes":        (33.5027163, -112.0820948),
    "baruptown":   (33.5171692, -112.0829403),
    "denny7th":    (33.5094971, -112.0652910),
    "harveys":     (33.5080052, -112.0479731),
}

def leg(a, b):
    la, lo = P[a]; lb, lob = P[b]
    url = f"{OSRM}{lo},{la};{lob},{lb}?overview=simplified&geometries=polyline"
    req = urllib.request.Request(url, headers={"User-Agent": "dinerz-drivez/1.0"})
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))
            if d.get("code") == "Ok":
                r = d["routes"][0]
                return {"mi": round(r["distance"] / 1609.344, 2), "geom": r["geometry"]}
        except Exception as e:
            print(f"  retry {a}->{b}: {e}")
        time.sleep(2)
    raise SystemExit(f"FAILED leg {a} -> {b}")

# Routes 02, 05, 06 and 07 were dropped: Lucky Boy (6pm Sat), Sunny's Diner (3pm)
# and Joe's Diner (2pm) all close before the 6:30pm Saturday start.
# route key -> ordered chain of point keys; "run" legs are between stops,
# "walk" legs are parking<->stop. chain = [park_start?, stop, stop, stop, park_end?]
ROUTES = {
    "r1": {"start": "palmgrove", "stops": ["eatup", "chopper", "fivediner"], "end": "totalwine"},
    "r3": {"start": "desertsun", "stops": ["bikini", "welcome", "macalpines"], "end": "azcenter"},
    "r4": {"start": "bethanytowne", "stops": ["sonicbethany", "dennysbethany", "skippers"], "end": "bethanysq"},
}

out = {}
for rid, r in ROUTES.items():
    print(f"== {rid}")
    stops = r["stops"]
    run_legs = []
    for a, b in zip(stops, stops[1:]):
        print(f"   run {a} -> {b}")
        run_legs.append(leg(a, b)); time.sleep(1.0)
    walk_start = walk_end = None
    if r["start"]:
        print(f"   walk-in {r['start']} -> {stops[0]}")
        walk_start = leg(r["start"], stops[0]); time.sleep(1.0)
    if r["end"]:
        print(f"   walk-out {stops[-1]} -> {r['end']}")
        walk_end = leg(stops[-1], r["end"]); time.sleep(1.0)
    out[rid] = {
        "stops": [{"key": k, "lat": P[k][0], "lon": P[k][1]} for k in stops],
        "startLot": {"key": r["start"], "lat": P[r["start"]][0], "lon": P[r["start"]][1]} if r["start"] else None,
        "endLot": {"key": r["end"], "lat": P[r["end"]][0], "lon": P[r["end"]][1]} if r["end"] else None,
        "runLegs": run_legs,
        "walkStart": walk_start,
        "walkEnd": walk_end,
        "runTotal": round(sum(l["mi"] for l in run_legs), 1),
    }
    print(f"   -> run total {out[rid]['runTotal']} mi")

with open("routes.json", "w") as f:
    json.dump(out, f)
print("\nSummary:")
for rid, r in out.items():
    ws = r["walkStart"]["mi"] if r["walkStart"] else "-"
    we = r["walkEnd"]["mi"] if r["walkEnd"] else "-"
    print(f"  {rid}: run {r['runTotal']} mi  legs={[l['mi'] for l in r['runLegs']]}  walkIn={ws} walkOut={we}")
