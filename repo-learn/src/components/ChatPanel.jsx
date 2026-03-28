import React, { useState, useEffect, useRef } from 'react';
import { X, Send, User, Bot, Sparkles } from 'lucide-react';
import './ChatPanel.css';

const MOCK_MESSAGES = [
  { id: 1, sender: 'bot', text: 'Hi! I am analyzing the `facebook/react` repository. What would you like to know about it?' },
  { id: 2, sender: 'user', text: 'Where is the reconciliation logic located?' },
  { id: 3, sender: 'bot', text: 'The core reconciliation logic is primarily located in `packages/react-reconciler`. The entry point for the work loop is `ReactFiberWorkLoop.js`. This is where React decides what parts of the DOM need to be updated during a render phase.' }
];

export default function ChatPanel({ isOpen, onClose }) {
  const [messages, setMessages] = useState(MOCK_MESSAGES);
  const [inputVal, setInputVal] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isOpen, messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    
    const newMsg = { id: Date.now(), sender: 'user', text: inputVal };
    setMessages(prev => [...prev, newMsg]);
    setInputVal('');

    // Mock bot reply
    setTimeout(() => {
      setMessages(prev => [
        ...prev, 
        { id: Date.now(), sender: 'bot', text: `You asked about "${newMsg.text}". In React, this pattern is highly optimized inside the \`react-reconciler\` module to ensure smooth scheduling and rendering flows.` }
      ]);
    }, 1000);
  };

  return (
    <div className={`chat-panel ${isOpen ? 'open' : ''}`}>
      <div className="chat-header">
        <div className="chat-title">
          <Sparkles size={18} color="var(--color-accent-blue)" />
          <span>Repo Assistant</span>
        </div>
        <button className="chat-close" onClick={onClose} aria-label="Close chat">
          <X size={20} />
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.sender}`}>
            <div className="message-avatar">
              {msg.sender === 'user' ? <User size={14} /> : <Bot size={14} color="white" />}
            </div>
            <div className="message-content">
              {msg.text.split('`').map((part, i) => 
                i % 2 === 1 ? <code key={i}>{part}</code> : part
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-area" onSubmit={handleSend}>
        <input 
          type="text" 
          className="chat-input"
          placeholder="Ask about this codebase..." 
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
        />
        <button type="submit" className="chat-send-btn" disabled={!inputVal.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
