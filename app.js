/* Route maps. Draws the real OSRM walking geometry baked into routes.js on a
   Leaflet map, one per route card, initialised lazily as cards scroll into view. */
(function () {
  'use strict';

  var DATA = window.ROUTE_DATA;
  if (!window.L || !DATA) return;

  var TILES = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
  var ATTRIB = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
               'contributors &copy; <a href="https://carto.com/attributions">CARTO</a> &middot; ' +
               'routing by <a href="https://project-osrm.org/">OSRM</a>';

  var RUN = '#D42A3C';
  var WALK = '#1B7F78';

  /* Standard encoded-polyline decoder (precision 5). */
  function decode(str) {
    var pts = [], i = 0, lat = 0, lng = 0;
    while (i < str.length) {
      var shift = 0, result = 0, b;
      do { b = str.charCodeAt(i++) - 63; result |= (b & 0x1f) << shift; shift += 5; } while (b >= 0x20);
      lat += (result & 1) ? ~(result >> 1) : (result >> 1);
      shift = 0; result = 0;
      do { b = str.charCodeAt(i++) - 63; result |= (b & 0x1f) << shift; shift += 5; } while (b >= 0x20);
      lng += (result & 1) ? ~(result >> 1) : (result >> 1);
      pts.push([lat * 1e-5, lng * 1e-5]);
    }
    return pts;
  }

  function puck(html, cls) {
    return L.divIcon({
      html: '<div class="pin ' + cls + '">' + html + '</div>',
      className: '',
      iconSize: [26, 26],
      iconAnchor: [13, 13],
      popupAnchor: [0, -14]
    });
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* Stop names/types/addresses live in the markup — read them back so the page
     content stays the single source of truth. */
  function readStops(card) {
    return Array.prototype.map.call(card.querySelectorAll('.stop'), function (el) {
      var tag = el.querySelector('.tag');
      var cls = /drivein|diner|dive/.exec(tag.className);
      return {
        name: el.querySelector('h4').textContent.trim(),
        type: tag.textContent.trim(),
        cls: cls ? cls[0] : 'diner',
        addr: el.querySelector('.addr').textContent.trim()
      };
    });
  }

  function readLots(card) {
    return Array.prototype.map.call(card.querySelectorAll('.park-box'), function (el) {
      return {
        kind: el.querySelector('.k').textContent.trim(),
        name: el.querySelector('.lot').childNodes[0].textContent.trim(),
        addr: el.querySelector('.lot .addr').textContent.trim()
      };
    });
  }

  function line(map, geom, color, dashed) {
    var pts = decode(geom);
    L.polyline(pts, { color: '#FFFBF0', weight: dashed ? 7 : 9, opacity: 0.9 }).addTo(map);
    L.polyline(pts, {
      color: color,
      weight: dashed ? 4 : 5,
      opacity: 1,
      dashArray: dashed ? '9 8' : null,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(map);
    return pts;
  }

  function build(el) {
    var id = el.dataset.route;
    var d = DATA[id];
    var card = el.closest('.route');
    if (!d || !card) return;

    var map = L.map(el, {
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true
    });
    L.tileLayer(TILES, { attribution: ATTRIB, maxZoom: 19, subdomains: 'abcd' }).addTo(map);

    // Let the page scroll past the map; a click hands the wheel to the map.
    map.on('click', function () { map.scrollWheelZoom.enable(); });
    map.on('mouseout', function () { map.scrollWheelZoom.disable(); });

    var all = [];
    if (d.walkStart) all = all.concat(line(map, d.walkStart.geom, WALK, true));
    d.runLegs.forEach(function (leg) { all = all.concat(line(map, leg.geom, RUN, false)); });
    if (d.walkEnd) all = all.concat(line(map, d.walkEnd.geom, WALK, true));

    var stops = readStops(card);
    d.stops.forEach(function (s, i) {
      var info = stops[i] || {};
      L.marker([s.lat, s.lon], { icon: puck(String(i + 1), info.cls || 'diner'), title: info.name })
        .addTo(map)
        .bindPopup(
          '<span class="t">Stop ' + (i + 1) + ' &middot; ' + esc(info.type || '') + '</span>' +
          '<b>' + esc(info.name || '') + '</b>' + esc(info.addr || '')
        );
      all.push([s.lat, s.lon]);
    });

    var lots = readLots(card);
    var lotIdx = 0;
    [['startLot', 0], ['endLot', 1]].forEach(function (pair) {
      var lot = d[pair[0]];
      if (!lot) { return; }
      var info = lots[pair[1]] || lots[lotIdx] || {};
      L.marker([lot.lat, lot.lon], { icon: puck('P', 'park'), title: info.name })
        .addTo(map)
        .bindPopup(
          '<span class="t">' + esc(info.kind || 'Parking') + '</span>' +
          '<b>' + esc(info.name || 'Parking') + '</b>' + esc(info.addr || '')
        );
      all.push([lot.lat, lot.lon]);
      lotIdx++;
    });

    map.fitBounds(L.latLngBounds(all), { padding: [28, 28] });
  }

  var maps = document.querySelectorAll('.map[data-route]');

  if (!('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(maps, build);
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      build(e.target);
    });
  }, { rootMargin: '300px 0px' });

  Array.prototype.forEach.call(maps, function (m) { io.observe(m); });
})();
