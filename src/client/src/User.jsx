import React, { useState, useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const WS_URL = "ws://localhost:8000/ws/";
// const WS_URL = "ws://127.0.0.1:8000/ws/";

const User = () => {
  const [map, setMap] = useState(null);
  const [route, setRoute] = useState(null);
  const [position, setPosition] = useState(null);
  const [wsResponder, setWsResponder] = useState(null);
  const [wsRequest, setWsRequest] = useState(null);
  const carMarkerRef = useRef(null);
  const routeRef = useRef(null);
  const user_lat = 41.310726;
  const user_lon = -72.929916;
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const mapInstance = L.map("map").setView([41.310726, -72.929916], 12);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(
      mapInstance,
    );
    setMap(mapInstance);
    return () => mapInstance.remove();
  }, []);

  useEffect(() => {
    const socket = new WebSocket(WS_URL + "request");

    socket.onopen = () => {
      console.log("WebSocket for User Response connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.position) {
        setPosition(data.position);
      }

      if (data.type === "route") {
        const route = data.route;
        console.log("Received route:", route);
        setRoute(route);
        drawRouteOnMap(route);
      }
    };

    setWsRequest(socket);

    return () => {
      socket.close();
    };
  }, [map]);

  const handleSubmit = () => {
    setSubmitted(true);
    if (wsRequest) {
      wsRequest.send(
        JSON.stringify({
          type: "request_help",
          user_lat: user_lat,
          user_lon: user_lon,
          timestamp: new Date().toISOString(), // Store timestamp
        }),
      );
    }
  };

  const drawRouteOnMap = (route) => {
    if (route && route.length > 0) {
      const latLngs = route.map((coords) => [coords[1], coords[0]]);
      if (routeRef.current) {
        routeRef.current.setLatLngs(latLngs); // Update existing polyline
      } else {
        routeRef.current = L.polyline(latLngs, { color: "blue" }).addTo(map);
      }

      map.setView(latLngs[0], 13);

      if (carMarkerRef.current) {
        carMarkerRef.current.setLatLng(latLngs[0]);
        carMarkerRef.current.bindPopup("Assigned Route").openPopup();
      } else {
        carMarkerRef.current = L.marker(latLngs[0], {
          icon: L.icon({
            iconUrl: "/Car-Emoji.png",
            iconSize: [30, 30],
            iconAnchor: [15, 15],
          }),
        })
          .addTo(map)
          .bindPopup("Assigned Route")
          .openPopup();
      }

      animateVehicle(latLngs);
    }
  };

  const animateVehicle = (route) => {
    let currentPosition = 0;

    const moveVehicle = () => {
      if (currentPosition < route.length) {
        const nextPos = route[currentPosition];
        if (carMarkerRef.current) {
          carMarkerRef.current.setLatLng(nextPos);
          map.setView(nextPos);
        }
        currentPosition += 1;
      } else {
        clearInterval(vehicleMoveInterval); // Stop animation when route is completed
      }
    };

    const vehicleMoveInterval = setInterval(moveVehicle, 1000); // Update every second
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "40vw",
      }}
    >
      <h1>User</h1>
      {!submitted && (
        <button onClick={handleSubmit}>Submit Help Request</button>
      )}

      <div id="map" style={{ height: "40vh", width: "40vh" }}></div>
    </div>
  );
};

export default User;
