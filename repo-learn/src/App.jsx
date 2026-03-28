import React, { useState } from 'react';
import { Routes, Route, useParams } from 'react-router-dom';
import HomeSearch from './components/HomeSearch';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import ChatPanel from './components/ChatPanel';
import FloatingChatButton from './components/FloatingChatButton';
import './App.css';

// Layout wrapper for Dashboard pages
function DashboardLayout() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const toggleChat = () => setIsChatOpen((prev) => !prev);
  const closeChat = () => setIsChatOpen(false);
  
  // Extract owner/repo from URL
  const { owner, repo } = useParams();
  const query = owner && repo ? `${owner}/${repo}` : '';

  return (
    <div className="app-container">
      <Sidebar />
      <div className={`main-area ${isChatOpen ? 'chat-open' : ''}`}>
        <Header 
          query={query} 
          onOpenChat={toggleChat} 
        />
        <main className="content-scroll">
          <Dashboard />
        </main>
      </div>
      <ChatPanel isOpen={isChatOpen} onClose={closeChat} />
      <FloatingChatButton onClick={toggleChat} isOpen={isChatOpen} />
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeSearch />} />
      <Route path="/analysis/:owner/:repo" element={<DashboardLayout />} />
    </Routes>
  );
}

export default App;
