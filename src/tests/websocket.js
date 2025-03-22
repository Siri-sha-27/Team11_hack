const socket = new WebSocket("ws://127.0.0.1:8000/ws/route");

socket.onopen = () => {
  console.log("WebSocket connection opened");
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received data:", data);
};

socket.onclose = () => {
  console.log("WebSocket connection closed");
};

socket.onerror = (error) => {
  console.log("WebSocket error:", error);
};
