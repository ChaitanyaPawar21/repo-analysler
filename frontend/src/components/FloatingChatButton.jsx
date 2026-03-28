import React from 'react';
import { MessageSquare } from 'lucide-react';

export default function FloatingChatButton({ onClick, isOpen }) {
  if (isOpen) return null; // Hide when chat is open
  
  return (
    <button 
      onClick={onClick}
      style={{
        position: 'absolute',
        bottom: '32px',
        right: '32px',
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        background: 'var(--color-accent-blue)',
        color: 'white',
        border: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 25px rgba(37, 99, 235, 0.4)',
        cursor: 'pointer',
        zIndex: 40,
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'scale(1.1)';
        e.currentTarget.style.boxShadow = '0 6px 30px rgba(37, 99, 235, 0.6)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.boxShadow = '0 4px 25px rgba(37, 99, 235, 0.4)';
      }}
      aria-label="Open Chat"
    >
      <MessageSquare size={24} />
    </button>
  );
}
