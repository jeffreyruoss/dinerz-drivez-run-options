#!/usr/bin/env python3
"""Geocode the four new routes and fetch real OSRM walking geometry for each leg."""
import json, time, urllib.request, urllib.parse

UA = "dinerz-drivez/1.0 (jeffreyruoss@gmail.com)"
OSRM = "https://router.project-osrm.org/route/v1/foot/"

ROUTES = {
    "r8": ["1343 W Broadway Rd, Tempe, AZ",
           "1015 W Broadway Rd, Tempe, AZ",
           "1122 E Broadway Rd, Tempe, AZ"],
    "r9": ["1343 W Broadway Rd, Tempe, AZ",
           "29 W Southern Ave, Tempe, AZ",
           "1122 E Broadway Rd, Tempe, AZ"],
    "r10": ["4829 E Indian School Rd, Phoenix, AZ",
            "2501 N 44th St, Phoenix, AZ",
            (33.4810632, -112.009958, "Sonic, 3330 E Thomas Ave, Phoenix (OSM node)")],
    "r11": ["235 W University Dr, Mesa, AZ",
            "635 N Country Club Dr, Mesa, AZ",
            "1210 E Main St, Mesa, AZ"],
}

cache = {}
def geocode(q):
    if isinstance(q, tuple):
        return q
    if q in cache:
        return cache[q]
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1, "countrycodes": "us"})
    r = json.load(urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30))
    time.sleep(1.1)
    if not r:
        raise SystemExit("geocode failed: " + q)
    cache[q] = (float(r[0]["lat"]), float(r[0]["lon"]), r[0]["display_name"])
    return cache[q]


def leg(a, b):
    url = f"{OSRM}{a[1]},{a[0]};{b[1]},{b[0]}?overview=simplified&geometries=polyline"
    for _ in range(4):
        try:
            d = json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40))
            if d.get("code") == "Ok":
                r = d["routes"][0]
                return {"mi": round(r["distance"] / 1609.344, 2), "geom": r["geometry"]}
        except Exception as e:
            print("   retry:", e)
        time.sleep(3)
    raise SystemExit("OSRM failed")


out = {}
for rid, addrs in ROUTES.items():
    print(f"\n== {rid}")
    pts = []
    for a in addrs:
        g = geocode(a)
        print(f"   {str(a)[:40]:42} -> {g[0]:.6f},{g[1]:.6f}  {g[2][:56]}")
        pts.append(g)
    legs = []
    for a, b in zip(pts, pts[1:]):
        legs.append(leg(a, b))
        time.sleep(1.0)
    out[rid] = {
        "stops": [{"key": str(addrs[i]), "lat": p[0], "lon": p[1]} for i, p in enumerate(pts)],
        "startLot": None, "endLot": None,
        "runLegs": legs, "walkStart": None, "walkEnd": None,
        "runTotal": round(sum(l["mi"] for l in legs), 1),
    }
    print(f"   legs={[l['mi'] for l in legs]}  total={out[rid]['runTotal']} mi")

json.dump(out, open("new_routes.json", "w"))
print("\nSUMMARY")
for rid, r in out.items():
    print(f"  {rid}: {r['runTotal']} mi   legs {[l['mi'] for l in r['runLegs']]}")
