import React, { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import ChatResponse from "./components/ChatResponse";
import AboutPage from "./components/AboutPage";
import useChatStore from "./store/chatStore";

export default function App() {

  const clearMessages = useChatStore((state)=>state.clearMessages);

  useEffect(()=>{
    clearMessages();
  }, [])

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/chat/response" element={<ChatResponse />} />
      {/* <Route path="/about" element={<AboutPage />} /> */}
    </Routes>
  );
}