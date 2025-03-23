import React, { useState, useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const WS_URL = "ws://localhost:8000/ws/";
// const WS_URL = "ws://127.0.0.1:8000/ws/";

const Responder = () => {
  const [userRequests, setUserRequests] = useState([]);
  const [activeRequest, setActiveRequest] = useState(null);
  const mapRef = useRef(null);
  const [map, setMap] = useState(null);
  const vehicleRef = useRef(null);
  const routeRef = useRef(null);
  const wsRef = useRef(null);
  const responder_lat = 41.320726;
  const responder_lon = -72.919916;
  const [route, setRoute] = useState(null);
  const [vehiclePosition, setVehiclePosition] = useState(null);
  const carMarkerRef = useRef(null);
  const [acceptedRequest, setAcceptedRequest] = useState(false);

  useEffect(() => {
    wsRef.current = new WebSocket(WS_URL + "respond");

    wsRef.current.onopen = () => console.log("Responder WebSocket connected");

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      console.log("Received WebSocket message:", data);

      if (data.type === "new_request") {
        const newRequest = {
          lat: data.user_lat,
          lon: data.user_lon,
          timestamp: data.timestamp,
        };
        setUserRequests(data.requests); // Add request to queue
      } else if (data.type === "route") {
        setRoute(data.route);
        console.log("Route:", data.route);
        drawRouteOnMap(data.route);
      }
    };

    wsRef.current.onclose = () => console.log("WebSocket closed by server.");
  }, []);

  useEffect(() => {
    if (!mapRef.current) {
      if (activeRequest) {
        console.log("Active Request:", activeRequest);
        mapRef.current = L.map("responder-map").setView(
          [activeRequest.lat, activeRequest.lon],
          13,
        );
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(
          mapRef.current,
        );
        L.marker([activeRequest.lat, activeRequest.lon])
          .addTo(mapRef.current)
          .bindPopup("User Location")
          .openPopup();
      } else {
        mapRef.current = L.map("responder-map").setView(
          [41.320726, -72.919916],
          12,
        );
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(
          mapRef.current,
        );
      }
    }
  }, [activeRequest]);

  const handleAcceptNext = () => {
    if (userRequests.length > 0) {
      const nextRequest = userRequests.shift();
      setActiveRequest(nextRequest);
      setUserRequests([...userRequests]); // Update queue state
      setAcceptedRequest(true);

      if (wsRef.current) {
        wsRef.current.send(
          JSON.stringify({
            type: "accept_request",
            responder_lat: responder_lat,
            responder_lon: responder_lon,
            user_lat: nextRequest.lat,
            user_lon: nextRequest.lon,
          }),
        );
      }
    }
  };

  const drawRouteOnMap = (route) => {
    if (route && route.length > 0) {
      const latLngs = route.map((coords) => [coords[1], coords[0]]);
      if (routeRef.current) {
        routeRef.current.setLatLngs(latLngs); // Update existing polyline
      } else {
        routeRef.current = L.polyline(latLngs, { color: "blue" }).addTo(
          mapRef.current,
        );
      }

      mapRef.current.setView(latLngs[0], 12);
      setMap(mapRef.current);

      setVehiclePosition(latLngs[0]); // Set initial vehicle position

      animateVehicle(latLngs);
    }
  };

  const animateVehicle = (route) => {
    let currentPosition = 0;

    const moveVehicle = () => {
      if (currentPosition < route.length) {
        const nextPos = route[currentPosition];
        setVehiclePosition(nextPos); // Update vehicle position
        currentPosition += 1;
      } else {
        clearInterval(vehicleMoveInterval); // Stop animation when route is completed
      }
    };

    const vehicleMoveInterval = setInterval(moveVehicle, 1000); // Update every second
  };

  useEffect(() => {
    if (map && vehiclePosition) {
      if (carMarkerRef.current) {
        map.removeLayer(carMarkerRef.current);
      }

      const newMarker = L.marker([vehiclePosition[0], vehiclePosition[1]], {
        icon: L.icon({
          iconUrl: "/Car-Emoji.png",
          iconSize: [30, 30],
          iconAnchor: [15, 15],
        }),
      })
        .addTo(map)
        .bindPopup("Car");

      carMarkerRef.current = newMarker;

      map.setView([vehiclePosition[0], vehiclePosition[1]]);
    }
  }, [map, vehiclePosition]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "40vw",
      }}
    >
      <h1>Responder</h1>

      {userRequests.length > 0 && (
        <button onClick={handleAcceptNext}>
          Accept Next Request ({userRequests.length} pending)
        </button>
      )}

      <div id="responder-map" style={{ height: "40vh", width: "40vh" }}></div>
    </div>
  );
};

export default Responder;
