import { useEffect, useState } from "react";
import Map, { Marker, Source, Layer } from "react-map-gl/mapbox";
// import Map, { Marker, Source, Layer } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";

// Replace with your Mapbox access token
const MAPBOX_TOKEN =
  "pk.eyJ1IjoianB3YXJyNyIsImEiOiJjbThrbTI5YncweWw5Mm9vZzZlcnRzcDN5In0.cz4Jo4SoWQ-1dNT-ZDuDXg";

// Starting & Ending Coordinates
const startPosition = [-122.42, 37.77]; // San Francisco Example
const endPosition = [-122.41, 37.78];

export default function App() {
  const [route, setRoute] = useState([]);
  const [position, setPosition] = useState(startPosition);
  const [viewport, setViewport] = useState({
    latitude: 37.77,
    longitude: -122.42,
    zoom: 14,
    bearing: 0,
    pitch: 0,
  });

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/route");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setPosition([data.lon, data.lat]);

      if (!data.completed) {
        setRoute((prev) => [...prev, [data.lon, data.lat]]);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <Map
      {...viewport}
      width="100%"
      height="500px"
      mapboxApiAccessToken={MAPBOX_TOKEN}
      onViewportChange={setViewport}
    >
      {/* Route Line */}
      <Source
        id="route"
        type="geojson"
        data={{
          type: "FeatureCollection",
          features: [
            {
              type: "Feature",
              geometry: { type: "LineString", coordinates: route },
            },
          ],
        }}
      >
        <Layer
          id="routeLayer"
          type="line"
          paint={{ "line-color": "#007cbf", "line-width": 4 }}
        />
      </Source>

      {/* Start & End Markers */}
      <Marker latitude={startPosition[1]} longitude={startPosition[0]}>
        <div>Start</div>
      </Marker>
      <Marker latitude={endPosition[1]} longitude={endPosition[0]}>
        <div>End</div>
      </Marker>

      {/* Moving Marker */}
      <Marker latitude={position[1]} longitude={position[0]}>
        <div>Current Position</div>
      </Marker>
    </Map>
  );
}
