import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Fade out the branded boot splash (index.html) once the app has mounted.
requestAnimationFrame(() => {
  const splash = document.getElementById("brand-splash");
  if (!splash) return;
  splash.style.opacity = "0";
  setTimeout(() => splash.remove(), 400);
});
