import React, { useState } from 'react';
import HomeSearch from './components/HomeSearch';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import ChatPanel from './components/ChatPanel';
import FloatingChatButton from './components/FloatingChatButton';

import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home' or 'dashboard'
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentView('dashboard');
  };

  const toggleChat = () => setIsChatOpen((prev) => !prev);
  const closeChat = () => setIsChatOpen(false);
  
  const goHome = () => setCurrentView('home');

  if (currentView === 'home') {
    return <HomeSearch onSearch={handleSearch} />;
  }

  return (
    <div className="app-container">
      <Sidebar onHomeClick={goHome} />
      <div className={`main-area ${isChatOpen ? 'chat-open' : ''}`}>
        <Header 
          query={searchQuery} 
          onOpenChat={toggleChat} 
          onHomeClick={goHome} 
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

export default App;
