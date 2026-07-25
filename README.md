# Dinerz, Drive-Inz & Divez — Route Options

Phoenix-area run routes, each hitting a sit-down **diner**, a **drive-in** you can go
inside, and a **dive bar** — with the running distance between the three stops shown
separately from the walk to and from parking.

Static site, 1950s diner styling. No build step.

## Scoped to a 6:30pm Saturday start

Every stop on the page is open for a 6:30pm Saturday start. Of the seven routes originally
scouted, four were cut for closing too early (Lucky Boy 6pm Sat took out two, Sunny's Diner
3pm and Joe's Diner 2pm one each) and four new ones were found to replace them. The result
is renumbered **01–07** in page order:

| # | Route | Run | Diner / Drive-in / Dive |
| --- | --- | --- | --- |
| 01 | Central Corridor | 4.5 mi | 5 & Diner / Eat Up / Chopper Johns |
| 02 | Grand Ave Loop | 3.8 mi | Welcome Diner / MacAlpine's / Bikini Lounge |
| 03 | Andrea's Westside | 1.6 mi | Denny's / Sonic / Skippers Lounge |
| 04 | Tempe Broadway | 2.5 mi | Denny's / Sonic / Palo Verde Lounge |
| 05 | Yucca / Southern | 4.8 mi | Denny's / Sonic / Yucca Tap Room |
| 06 | Arcadia 44th St | 4.0 mi | IHOP / Sonic / JT's Bar & Grill |
| 07 | Mesa Country Club | 3.3 mi | Denny's / Sonic / Gabby's |

Route 02 is the tight one — MacAlpine's is its last stop and closes at 8pm.

### How routes 04–07 were found

1. Pulled every bar, pub, restaurant and fast-food venue in the Phoenix metro from
   OpenStreetMap via Overpass (`scripts/find_candidates.py` territory — the query lives in
   the commit history).
2. Cross-referenced the bar list against published Phoenix dive-bar guides, since OSM has
   no "dive" tag and only ~15% of its bars carry `opening_hours`.
3. Clustered each dive against the nearest late-night diner and drive-in.
4. Verified Saturday hours for every surviving venue individually before adding it. This
   step killed a North Phoenix route — the Sonic at 17238 N 19th Ave is listed as
   permanently closed.

## What's here

| File | Purpose |
| --- | --- |
| `index.html` | All seven routes — stops, hours, parking, links |
| `styles.css` | Diner theme (neon hero, chrome trim, menu board, scalloped awning) |
| `app.js` | Draws each route map with Leaflet, lazily as cards scroll into view |
| `routes.js` | Baked-in route geometry + distances (generated — see below) |
| `vendor/leaflet/` | Leaflet 1.9.4, vendored so the page has no CDN dependency |
| `scripts/build_routes.py` | Regenerates the route data |

## Distances are real, not straight-line

Every mileage on the page is a **street-following walking route**, not a straight-line
estimate:

- Stop and parking-lot coordinates were geocoded from their street addresses via
  [Nominatim](https://nominatim.openstreetmap.org/).
- Each leg was routed with the [OSRM](https://project-osrm.org/) `foot` profile, and the
  resulting geometry and distance baked into `routes.js`.

Maps render that exact geometry over [CARTO](https://carto.com/) basemap tiles. The
**Run directions** buttons hand off to Google Maps for live turn-by-turn.

## Regenerating route data

Edit the stop coordinates or route definitions in `scripts/build_routes.py`, then:

```bash
cd scripts && python3 build_routes.py     # writes routes.json
```

Convert the JSON to the `routes.js` module the page loads:

```bash
python3 -c "
import json
d = json.load(open('routes.json'))
open('../routes.js','w').write('window.ROUTE_DATA = ' + json.dumps(d) + ';\n')
"
```

The script is deliberately polite to the public OSRM demo server (~1 request/second).
Mileages shown in `index.html` are written by hand from the script's summary output —
update both if you change a route.

## Running locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.
