import React from "react";
import { Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import ChatResponse from "./components/ChatResponse";
import AboutPage from "./components/AboutPage";

export default function App() {
  return (
    <Routes>
      <Route path="/chat" element={<LandingPage />} />
      <Route path="/chat/response" element={<ChatResponse />} />
      <Route path="/about" element={<AboutPage />} />
    </Routes>

  );
}