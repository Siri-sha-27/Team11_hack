import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { WebSocketProvider } from "./WebSocketContext"; // Import the WebSocket provider

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

// // src/index.jsx
// import React from "react";
// import ReactDOM from "react-dom";
// import App from "./App";
// import { WebSocketProvider } from "./WebSocketContext"; // Import the WebSocket provider
//
// ReactDOM.render(
//   <WebSocketProvider>
//     <App />
//   </WebSocketProvider>,
//   document.getElementById("root"),
// );
