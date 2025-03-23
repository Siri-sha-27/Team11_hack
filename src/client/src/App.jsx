import React, { useState, useEffect, useRef } from "react";
import User from "./User";
import Responder from "./Responder";

const App = () => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "100vw",
      }}
    >
      <div>
        <h1>AI Response System (AIRS)</h1>
      </div>
      <div style={{ display: "flex", columns: "2" }}>
        <User />
        <Responder />
      </div>
    </div>
  );
};

export default App;
