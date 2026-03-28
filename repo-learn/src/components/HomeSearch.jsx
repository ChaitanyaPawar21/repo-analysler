import React, { useRef, useState } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { Terminal, Search, Code, Cpu } from 'lucide-react';
import './HomeSearch.css';

export default function HomeSearch({ onSearch }) {
  const containerRef = useRef(null);
  const [query, setQuery] = useState('');

  useGSAP(() => {
    const tl = gsap.timeline();
    tl.fromTo('.home-logo', { scale: 0.8, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.8, ease: 'back.out(1.5)' })
      .fromTo('.home-title', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }, '-=0.4')
      .fromTo('.home-subtitle', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }, '-=0.4')
      .fromTo('.search-bar-container', { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }, '-=0.2')
      .fromTo('.quick-chips', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, stagger: 0.1, ease: 'power2.out' }, '-=0.2');
  }, { scope: containerRef });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  const handleChipClick = (repo) => {
    setQuery(repo);
    onSearch(repo);
  };

  return (
    <div className="home-search-wrapper" ref={containerRef}>
      <div className="home-content-box">
        <div className="home-logo">
          <Terminal size={64} className="logo-icon" />
        </div>
        <h1 className="home-title">Repo-Learn AI</h1>
        <p className="home-subtitle">Paste a GitHub URL or search a popular repository to instantly understand its architecture.</p>

        <form onSubmit={handleSubmit} className="search-bar-container">
          <div className="search-input-wrapper">
            <Search className="search-icon-left" size={20} />
            <input 
              type="text" 
              placeholder="e.g. facebook/react" 
              className="home-search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
            />
            <button type="submit" className="search-btn-right">Analyze</button>
          </div>
        </form>

        <div className="quick-chips-wrapper">
          <p className="quick-chips-title">Or try a popular repo</p>
          <div className="chips-row">
            <button className="quick-chips" onClick={() => handleChipClick('facebook/react')}>
              <Code size={14} /> React
            </button>
            <button className="quick-chips" onClick={() => handleChipClick('vercel/next.js')}>
              <Terminal size={14} /> Next.js
            </button>
            <button className="quick-chips" onClick={() => handleChipClick('vuejs/core')}>
              <Cpu size={14} /> Vue Core
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
