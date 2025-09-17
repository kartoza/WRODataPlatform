const mapContainer = document.getElementById("map");

// Init Leaflet map
const map = L.map(mapContainer).setView([-29.064594, 24.619973], 5);

// Add basemap (OpenStreetMap via Carto Light)
L.tileLayer("https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors &copy; <a href='https://carto.com/'>CARTO</a>",
subdomains: "abcd",
maxZoom: 19
}).addTo(map);



// Feature group to store drawn items
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const stored = window.localStorage.getItem("geo_bounds");
if (stored) {
  let parsed;

  try {
    parsed = JSON.parse(stored);
  } catch (e) {
    console.error("Invalid JSON:", e);
    parsed = null;
  }

  if (parsed) {
    // Handle GeoJSON geometry
    if (parsed.type && parsed.coordinates) {
      const layer = L.geoJSON(parsed, {
        style: { color: "#4682b4", weight: 2 }
      }).addTo(map);

      // Zoom to bounds
      map.fitBounds(layer.getBounds());
      drawnItems.addLayer(layer);
    }
    // Fallback: handle old CSV-based storage
    else if (typeof stored === "string" && stored.includes(",")) {
      const coords = stored.split(",").map(parseFloat);

      if (coords.length === 4) {
        const bounds = L.latLngBounds(
          [coords[0], coords[1]],
          [coords[2], coords[3]]
        );
        const rect = L.rectangle(bounds, { color: "#4682b4", weight: 2 });
        rect.addTo(map);
        map.fitBounds(bounds);
        drawnItems.addLayer(rect);
      } else if (coords.length === 2) {
        const marker = L.marker([coords[0], coords[1]]);
        marker.addTo(map);
        map.setView([coords[0], coords[1]], 8);
        drawnItems.addLayer(marker);
      }
    }
  }
}

// Add draw controls (rectangle + marker only)
const drawControl = new L.Control.Draw({
  draw: {
    polygon: false,
    polyline: false,
    circle: false,
    circlemarker: false,
    rectangle: {
      shapeOptions: {
        color: "#4682b4",
        weight: 2
      }
    },
    marker: {
      icon: L.icon({
        iconUrl: "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png",
        iconSize: [20, 32],
        iconAnchor: [10, 32]
      })
    }
  },
  edit: {
    featureGroup: drawnItems
  }
});
map.addControl(drawControl);


// Handle draw events
map.on(L.Draw.Event.CREATED, function (e) {
  const layer = e.layer;
  drawnItems.addLayer(layer);

  if (e.layerType === "rectangle") {
    const bounds = layer.getBounds();
    const northEast = bounds.getNorthEast();
    const southWest = bounds.getSouthWest();
    const northWest = [northEast.lat, southWest.lng];
    const southEast = [southWest.lat, northEast.lng];
    const storedBounds = [...northWest, ...southEast];

    window.localStorage.setItem("geo_bounds", storedBounds);
    console.log("Rectangle bounds:", storedBounds);

  } else if (e.layerType === "marker") {
    const position = layer.getLatLng();
    const storedBounds = [position.lat, position.lng];

    window.localStorage.setItem("geo_bounds", storedBounds);
    console.log("Marker position:", storedBounds);
  }
});