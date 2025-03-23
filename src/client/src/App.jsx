import React, { useState, useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const MAPBOX_TOKEN =
  "pk.eyJ1IjoianB3YXJyNyIsImEiOiJjbThrbTI5YncweWw5Mm9vZzZlcnRzcDN5In0.cz4Jo4SoWQ-1dNT-ZDuDXg";

const WS_URL = "ws://localhost:8000/ws/";

const App = () => {
  const [map, setMap] = useState(null);
  const [route, setRoute] = useState([]);
  const [position, setPosition] = useState(null);
  const [start, setStart] = useState(null);
  const [end, setEnd] = useState(null);
  const [wsRoute, setWsRoute] = useState(null);
  const [wsDrive, setWsDrive] = useState(null);
  const carMarkerRef = useRef(null);

  // Initialize map
  useEffect(() => {
    const mapInstance = L.map("map").setView([37.77, -122.42], 12); // Default to San Francisco
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(
      mapInstance,
    );

    setMap(mapInstance);

    return () => mapInstance.remove();
  }, []);

  // WebSocket connection to Python FastAPI server
  useEffect(() => {
    const socket = new WebSocket(WS_URL + "route");

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.route) {
        setRoute(data.route);
        setStart(data.route[0]);
        setEnd(data.route[data.route.length - 1]);
      }
      if (data.position) {
        setPosition(data.position);
      }
    };

    setWsRoute(socket);

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    const socket = new WebSocket(WS_URL + "drive");

    socket.onopen = () => {
      console.log("WebSocket for drive connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.position) {
        setPosition(data.position);
      }
    };

    setWsDrive(socket);

    return () => {
      socket.close();
    };
  }, []);

  const handleSubmit = () => {
    if (wsRoute && wsRoute.readyState === WebSocket.OPEN) {
      wsRoute.send(
        JSON.stringify({
          start_lon: -122.42,
          start_lat: 37.77,
          end_lon: -122.37,
          end_lat: 37.78,
        }),
      );
    } else {
      console.error("WebSocket for route is not connected");
    }
  };

  const handleBeginDrive = () => {
    if (wsDrive && wsDrive.readyState === WebSocket.OPEN) {
      wsDrive.send(
        JSON.stringify({
          start_lon: -122.42,
          start_lat: 37.77,
          end_lon: -122.37,
          end_lat: 37.78,
        }),
      );
    } else {
      console.error("WebSocket for drive is not connected");
    }
  };

  useEffect(() => {
    if (map && route.length > 0) {
      const latlngs = route.map((coord) => [coord[1], coord[0]]);
      L.polyline(latlngs, { color: "blue" }).addTo(map);

      if (start) {
        L.marker([start[1], start[0]]).addTo(map).bindPopup("Start");
      }

      if (end) {
        L.marker([end[1], end[0]]).addTo(map).bindPopup("End");
      }
    }
  }, [map, route, start, end]);

  useEffect(() => {
    if (map && position) {
      // Remove previous marker if it exists
      if (carMarkerRef.current) {
        map.removeLayer(carMarkerRef.current);
      }

      // Create a new marker and store it in the ref
      const newMarker = L.marker([position[1], position[0]], {
        icon: L.divIcon({ className: "car-icon", html: "🚗" }),
      })
        .addTo(map)
        .bindPopup("Car");

      carMarkerRef.current = newMarker;

      // Center the map on the new position
      map.setView([position[1], position[0]]);
    }
  }, [map, position]);

  return (
    <div
      style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
    >
      <div>
        <button onClick={handleSubmit}>Submit Route</button>
        <button onClick={handleBeginDrive}>Begin Drive</button>
      </div>
      <div
        id="map"
        style={{ display: "flex", height: "50vh", width: "50vw" }}
      ></div>
    </div>
  );
};

export default App;
