# Dinerz, Drive-Inz & Divez — Route Options

Phoenix-area run routes, each hitting a sit-down **diner**, a **drive-in** you can go
inside, and a **dive bar** — with the running distance between the three stops shown
separately from the walk to and from parking.

Static site, 1950s diner styling. No build step.

## Scoped to a 6:30pm Saturday start

Seven routes were scouted; the page shows the **three** where all three stops are still
open at 6:30pm on a Saturday. Dropped: routes 02 and 07 (Lucky Boy closes 6pm Sat),
05 (Sunny's Diner, 3pm) and 06 (Joe's Diner, 2pm). Route numbering is unchanged so the
surviving routes keep the names people already know them by.

Route 03 is the tight one — MacAlpine's is its last stop and closes at 8pm.

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
