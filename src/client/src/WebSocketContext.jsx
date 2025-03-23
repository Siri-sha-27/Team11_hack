// src/WebSocketContext.js
import React, { createContext, useState, useEffect, useContext } from "react";

// Create a WebSocket context
const WebSocketContext = createContext(null);

// Create a custom hook to use the WebSocket context
export const useWebSocket = () => {
  return useContext(WebSocketContext);
};

// WebSocket provider to manage WebSocket connection
export const WebSocketProvider = ({ children }) => {
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/route");

    socket.onopen = () => {
      console.log("WebSocket connection established");
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, []);

  return (
    <WebSocketContext.Provider value={ws}>{children}</WebSocketContext.Provider>
  );
};
