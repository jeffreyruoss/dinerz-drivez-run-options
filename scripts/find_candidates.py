#!/usr/bin/env python3
"""Pull diner / drive-in / bar candidates across the Phoenix metro from OSM.

Queries by indexed amenity tag only (name regexes make Overpass crawl), then
filters client-side.
"""
import json, re, time, urllib.request, urllib.parse

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.jp/api/interpreter",
]
BBOX = "33.28,-112.32,33.72,-111.78"   # S,W,N,E — Phoenix, Glendale, Tempe, Scottsdale, Mesa


def fetch(query):
    last = None
    for ep in ENDPOINTS:
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    ep,
                    data=urllib.parse.urlencode({"data": query}).encode(),
                    headers={"User-Agent": "dinerz-drivez/1.0 (jeffreyruoss@gmail.com)"},
                )
                return json.load(urllib.request.urlopen(req, timeout=240))["elements"]
            except Exception as e:
                last = e
                print(f"   {ep.split('/')[2]} attempt {attempt+1}: {e}")
                time.sleep(5)
    raise SystemExit(f"all endpoints failed: {last}")


def norm(els):
    out = []
    for e in els:
        t = e.get("tags", {})
        name = t.get("name")
        lat = e.get("lat") or (e.get("center") or {}).get("lat")
        lon = e.get("lon") or (e.get("center") or {}).get("lon")
        if not name or lat is None:
            continue
        out.append({
            "name": name, "lat": lat, "lon": lon,
            "amenity": t.get("amenity"), "cuisine": t.get("cuisine", ""),
            "hours": t.get("opening_hours", ""),
            "street": (t.get("addr:housenumber", "") + " " + t.get("addr:street", "")).strip(),
            "city": t.get("addr:city", ""),
            "website": t.get("website", "") or t.get("contact:website", ""),
            "drive_in": t.get("drive_in", ""), "drive_through": t.get("drive_through", ""),
        })
    return out


def dedupe(items):
    seen, uniq = set(), []
    for o in sorted(items, key=lambda x: (-len(x["street"]), -len(x["hours"]))):
        k = (o["name"].lower(), round(o["lat"], 3), round(o["lon"], 3))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(o)
    return uniq


print("== bars & pubs")
bars = dedupe(norm(fetch(f'[out:json][timeout:180];nwr["amenity"~"^(bar|pub)$"]({BBOX});out center tags;')))
print("  ", len(bars))

print("== restaurants & fast food")
food = dedupe(norm(fetch(f'[out:json][timeout:180];nwr["amenity"~"^(restaurant|fast_food)$"]({BBOX});out center tags;')))
print("  ", len(food))

DINER = re.compile(r"\bdiner\b|\bgrill\b.*\bdiner\b", re.I)
DRIVE = re.compile(r"drive[\s\-]?in|sonic|\bdrive[\s\-]?thru\b", re.I)

diners = [f for f in food if DINER.search(f["name"]) or "diner" in f["cuisine"].lower()]
drives = [f for f in food if DRIVE.search(f["name"]) or f["drive_in"] == "yes"]

json.dump({"bars": bars, "diners": diners, "drives": drives, "food": food},
          open("candidates.json", "w"))
print(f"\ndiners: {len(diners)}   drive-ins: {len(drives)}   bars: {len(bars)}")
for label, arr in (("DINERS", diners), ("DRIVE-INS", drives)):
    print(f"\n--- {label} ---")
    for d in sorted(arr, key=lambda x: x["name"]):
        print(f"  {d['name'][:38]:40} {d['street'][:26]:28} {d['city'][:12]:13} {d['hours'][:34]}")
